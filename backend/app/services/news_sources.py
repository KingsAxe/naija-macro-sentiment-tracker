from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass
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
MIN_CONTENT_LENGTH = 80

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
class NewsArticleCandidate:
    source: str
    title: str
    url: str
    summary: str
    published_at: datetime | None
    topic_label: str | None


@dataclass(frozen=True, slots=True)
class NewsArticle:
    source: str
    title: str
    url: str
    summary: str
    published_at: datetime | None
    topic_label: str
    content: str


@dataclass(slots=True)
class NewsQualityReport:
    source: str
    fetched_count: int
    macro_candidate_count: int
    accepted_count: int
    rejected_count: int
    duplicate_url_count: int
    short_content_count: int
    missing_topic_count: int
    topic_coverage: dict[str, int]


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


def parse_feed_candidates(source: NewsSource, feed_xml: str) -> list[NewsArticleCandidate]:
    root = ElementTree.fromstring(feed_xml)
    items = root.findall(".//item")
    candidates: list[NewsArticleCandidate] = []

    for item in items:
        title = normalize_whitespace(item.findtext("title") or "")
        url = normalize_whitespace(item.findtext("link") or "")
        summary = strip_html(item.findtext("description") or "")
        published_at = parse_published_at(item.findtext("pubDate"))
        topic_label = classify_macro_topic(f"{title} {summary}")
        if not title or not url:
            continue
        candidates.append(
            NewsArticleCandidate(
                source=source.source,
                title=title,
                url=url,
                summary=summary,
                published_at=published_at,
                topic_label=topic_label,
            )
        )

    return candidates


def extract_article_text(html: str) -> str:
    parser = ParagraphExtractor()
    parser.feed(html)
    return normalize_whitespace(" ".join(parser.paragraphs))[:MAX_ARTICLE_CHARS]


def enrich_candidates_with_page_text(
    candidates: list[NewsArticleCandidate],
    *,
    fetch_pages: bool,
    logger: logging.Logger | None = None,
) -> list[NewsArticle]:
    articles: list[NewsArticle] = []
    for candidate in candidates:
        base_content = normalize_whitespace(f"{candidate.title}. {candidate.summary}")
        content = base_content

        if fetch_pages:
            try:
                page_text = extract_article_text(fetch_url(candidate.url))
            except (URLError, TimeoutError, OSError, ValueError) as exc:
                if logger:
                    logger.warning(
                        "Article fetch failed | source=%s | url=%s | error=%s",
                        candidate.source,
                        candidate.url,
                        exc,
                    )
                page_text = ""
            if page_text:
                content = normalize_whitespace(f"{candidate.title}. {page_text}")

        if candidate.topic_label is None:
            continue

        articles.append(
            NewsArticle(
                source=candidate.source,
                title=candidate.title,
                url=candidate.url,
                summary=candidate.summary,
                published_at=candidate.published_at,
                topic_label=candidate.topic_label,
                content=content,
            )
        )

    return articles


def validate_news_articles(
    candidates: list[NewsArticleCandidate],
    *,
    fetch_pages: bool,
    logger: logging.Logger | None = None,
) -> tuple[list[NewsArticle], NewsQualityReport]:
    enriched = enrich_candidates_with_page_text(candidates, fetch_pages=fetch_pages, logger=logger)
    accepted: list[NewsArticle] = []
    seen_urls: set[str] = set()
    duplicate_url_count = 0
    short_content_count = 0
    topic_coverage: dict[str, int] = {}

    for article in enriched:
        if article.url in seen_urls:
            duplicate_url_count += 1
            continue
        seen_urls.add(article.url)

        if len(article.content) < MIN_CONTENT_LENGTH:
            short_content_count += 1
            continue

        topic_coverage[article.topic_label] = topic_coverage.get(article.topic_label, 0) + 1
        accepted.append(article)

    report = NewsQualityReport(
        source=candidates[0].source if candidates else "unknown",
        fetched_count=len(candidates),
        macro_candidate_count=len(enriched),
        accepted_count=len(accepted),
        rejected_count=duplicate_url_count + short_content_count,
        duplicate_url_count=duplicate_url_count,
        short_content_count=short_content_count,
        missing_topic_count=sum(1 for candidate in candidates if candidate.topic_label is None),
        topic_coverage=topic_coverage,
    )
    return accepted, report


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
        candidates = parse_feed_candidates(source, fetch_url(source.feed_url))[:limit]
        articles, report = validate_news_articles(candidates, fetch_pages=fetch_pages, logger=logger)
        cleaned = articles_to_dataframe(articles)
        ingested_count, skipped_count = bulk_insert_clean_records(session=session, cleaned=cleaned)
        qa_summary = asdict(report)
        qa_summary["duplicate_count"] = skipped_count

        _mark_ingestion_run_completed(
            session=session,
            run=run,
            source_name=source.source,
            fetched_count=report.fetched_count,
            inserted_count=ingested_count,
            skipped_count=skipped_count,
            rejected_count=report.rejected_count + report.missing_topic_count,
            qa_summary=qa_summary,
        )
        if logger:
            logger.info(
                "News ingestion complete | run_id=%s | source=%s | inserted=%s | duplicates=%s | rejected=%s",
                run.id,
                source.source,
                ingested_count,
                skipped_count,
                report.rejected_count + report.missing_topic_count,
            )
        return IngestionRunResult(
            run_id=run.id,
            source_file=source.feed_url,
            source_name=source.source,
            fetched_count=report.fetched_count,
            ingested_count=ingested_count,
            skipped_count=skipped_count,
            duplicate_count=skipped_count,
            rejected_count=report.rejected_count + report.missing_topic_count,
            qa_summary=json.dumps(qa_summary, sort_keys=True),
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
