from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
from urllib.error import URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree

import pandas as pd
from sqlalchemy.orm import Session

from app.services.ingestion import (
    LAGOS_TZ,
    IngestionRunResult,
    _create_ingestion_run,
    _mark_ingestion_run_completed,
    _mark_ingestion_run_failed,
    bulk_insert_clean_records,
)

REQUEST_TIMEOUT_SECONDS = 20
USER_AGENT = "NaijaMacroSentimentTracker/0.1 (+local research project)"
MAX_ARTICLE_CHARS = 8000

TOPIC_KEYWORDS = {
    "FX Rate": (
        "cbn",
        "dollar",
        "exchange rate",
        "forex",
        "fx",
        "naira",
    ),
    "Food Inflation": (
        "agriculture",
        "food",
        "food prices",
        "inflation",
        "rice",
    ),
    "Fuel Price": (
        "diesel",
        "fuel",
        "nnpc",
        "oil",
        "petrol",
        "subsidy",
    ),
}


@dataclass(frozen=True, slots=True)
class NewsSource:
    source: str
    feed_url: str


NEWS_SOURCES = (
    NewsSource(source="vanguard", feed_url="https://www.vanguardngr.com/category/business/feed/"),
    NewsSource(source="punch", feed_url="https://rss.punchng.com/v1/category/business"),
)


@dataclass(frozen=True, slots=True)
class NewsArticle:
    source: str
    title: str
    url: str
    summary: str
    published_at: datetime | None
    topic_label: str
    content: str


class ParagraphExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_paragraph = False
        self._parts: list[str] = []
        self.paragraphs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "p":
            self._in_paragraph = True
            self._parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "p" and self._in_paragraph:
            paragraph = normalize_whitespace(" ".join(self._parts))
            if len(paragraph) > 40:
                self.paragraphs.append(paragraph)
            self._in_paragraph = False
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._in_paragraph:
            self._parts.append(data)


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(value)).strip()


def strip_html(value: str) -> str:
    return normalize_whitespace(re.sub(r"<[^>]+>", " ", value))


def classify_macro_topic(text: str) -> str | None:
    haystack = text.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(re.search(rf"\b{re.escape(keyword)}\b", haystack) for keyword in keywords):
            return topic
    return None


def fetch_url(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_feed_items(source: NewsSource, feed_xml: str) -> list[NewsArticle]:
    root = ElementTree.fromstring(feed_xml)
    items = root.findall(".//item")
    articles: list[NewsArticle] = []

    for item in items:
        title = normalize_whitespace(item.findtext("title") or "")
        url = normalize_whitespace(item.findtext("link") or "")
        summary = strip_html(item.findtext("description") or "")
        published_at = parse_published_at(item.findtext("pubDate"))
        topic_label = classify_macro_topic(f"{title} {summary}")
        if not title or not url or topic_label is None:
            continue
        articles.append(
            NewsArticle(
                source=source.source,
                title=title,
                url=url,
                summary=summary,
                published_at=published_at,
                topic_label=topic_label,
                content=normalize_whitespace(f"{title}. {summary}"),
            )
        )

    return articles


def parse_published_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=LAGOS_TZ)
    return parsed.astimezone(LAGOS_TZ)


def extract_article_text(html: str) -> str:
    parser = ParagraphExtractor()
    parser.feed(html)
    return normalize_whitespace(" ".join(parser.paragraphs))[:MAX_ARTICLE_CHARS]


def enrich_articles_with_page_text(
    articles: list[NewsArticle],
    logger: logging.Logger | None = None,
) -> list[NewsArticle]:
    enriched: list[NewsArticle] = []
    for article in articles:
        content = article.content
        try:
            page_text = extract_article_text(fetch_url(article.url))
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            if logger:
                logger.warning("Article fetch failed | source=%s | url=%s | error=%s", article.source, article.url, exc)
            page_text = ""

        if page_text:
            content = normalize_whitespace(f"{article.title}. {page_text}")
        enriched.append(
            NewsArticle(
                source=article.source,
                title=article.title,
                url=article.url,
                summary=article.summary,
                published_at=article.published_at,
                topic_label=article.topic_label,
                content=content,
            )
        )
    return enriched


def articles_to_dataframe(articles: list[NewsArticle]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "source": article.source,
                "topic_label": article.topic_label,
                "content": article.content,
                "published_at": article.published_at,
                "source_url": article.url,
            }
            for article in articles
        ]
    )


def ingest_news_source(
    session: Session,
    source: NewsSource,
    *,
    limit: int = 20,
    fetch_pages: bool = True,
    logger: logging.Logger | None = None,
) -> IngestionRunResult:
    run = _create_ingestion_run(session=session, source_type="news_feed", source_file=source.feed_url)
    try:
        articles = parse_feed_items(source, fetch_url(source.feed_url))[:limit]
        if fetch_pages:
            articles = enrich_articles_with_page_text(articles, logger=logger)
        cleaned = articles_to_dataframe(articles)
        ingested_count, skipped_count = bulk_insert_clean_records(session=session, cleaned=cleaned)
        _mark_ingestion_run_completed(
            session=session,
            run=run,
            source_name=source.source,
            inserted_count=ingested_count,
            skipped_count=skipped_count,
        )
        if logger:
            logger.info(
                "News ingestion complete | run_id=%s | source=%s | inserted=%s | duplicates=%s",
                run.id,
                source.source,
                ingested_count,
                skipped_count,
            )
        return IngestionRunResult(
            run_id=run.id,
            source_file=source.feed_url,
            source_name=source.source,
            ingested_count=ingested_count,
            skipped_count=skipped_count,
            duplicate_count=skipped_count,
        )
    except Exception as exc:
        _mark_ingestion_run_failed(session=session, run=run, error=exc)
        raise


def ingest_news_sources(
    session: Session,
    *,
    limit_per_source: int = 20,
    fetch_pages: bool = True,
    logger: logging.Logger | None = None,
) -> list[IngestionRunResult]:
    results: list[IngestionRunResult] = []
    for source in NEWS_SOURCES:
        results.append(
            ingest_news_source(
                session=session,
                source=source,
                limit=limit_per_source,
                fetch_pages=fetch_pages,
                logger=logger,
            )
        )
    return results
