from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
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
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
)
DEFAULT_REQUEST_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}
SOURCE_PAGE_REQUEST_HEADERS = {
    "vanguard": {
        "Referer": "https://www.vanguardngr.com/category/business/",
    },
    "punch": {
        "Referer": "https://punchng.com/topics/business/",
    },
}
MAX_ARTICLE_CHARS = 8000
MIN_CONTENT_LENGTH = 80
MAX_REJECTED_SAMPLES = 5

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
        "grain",
        "harvest",
        "rice",
        "tomato",
    ),
    "Fuel Price": (
        "diesel",
        "fuel",
        "kerosene",
        "nnpc",
        "oil",
        "petrol",
        "subsidy",
    ),
    "Monetary Policy": (
        "cash reserve ratio",
        "cbn policy",
        "liquidity ratio",
        "monetary policy",
        "monetary tightening",
        "mpc",
        "open market operations",
    ),
    "Interest Rates": (
        "benchmark rate",
        "borrowing costs",
        "interest rate",
        "lending rate",
        "loan rate",
        "mpr",
        "treasury bill yield",
    ),
    "Cost of Living": (
        "consumer prices",
        "cost of living",
        "cpi",
        "household costs",
        "inflation",
        "living costs",
        "purchasing power",
    ),
    "Power/Energy": (
        "electricity",
        "energy",
        "gas supply",
        "grid",
        "power sector",
        "power supply",
        "tariff",
        "transmission line",
    ),
    "Trade/Imports": (
        "customs duty",
        "exports",
        "import duty",
        "imports",
        "port charges",
        "trade balance",
        "trade flows",
    ),
    "Banking/Credit": (
        "bank lending",
        "banking sector",
        "credit growth",
        "credit to private sector",
        "loan book",
        "loan default",
        "non-performing loans",
    ),
    "Budget/Fiscal Policy": (
        "appropriation bill",
        "budget deficit",
        "capital expenditure",
        "fiscal policy",
        "government spending",
        "public debt",
        "tax revenue",
    ),
    "Transport/Logistics": (
        "freight",
        "haulage",
        "logistics",
        "port congestion",
        "shipping costs",
        "transport fares",
        "trucking",
    ),
    "Employment/Labour": (
        "job creation",
        "labour",
        "minimum wage",
        "salary arrears",
        "unemployment",
        "wage bill",
        "workers union",
    ),
    "Business Confidence/Private Sector": (
        "business confidence",
        "factory output",
        "investor confidence",
        "manufacturing output",
        "private sector",
        "pmi",
        "purchasing managers' index",
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
    page_fetch_success_count: int
    page_fetch_forbidden_count: int
    page_fetch_error_count: int
    topic_coverage: dict[str, int]
    rejected_samples: list[dict[str, str]]


@dataclass(frozen=True, slots=True)
class RejectedNewsSample:
    title: str
    source: str
    url: str | None
    rejection_reason: str


@dataclass(frozen=True, slots=True)
class PageFetchMetrics:
    success_count: int = 0
    forbidden_count: int = 0
    error_count: int = 0


def build_request_headers(*, source: str | None = None, is_feed: bool = False) -> dict[str, str]:
    headers = dict(DEFAULT_REQUEST_HEADERS)
    if is_feed:
        headers["Accept"] = "application/rss+xml,application/xml;q=0.9,text/xml;q=0.8,*/*;q=0.7"
    if source:
        headers.update(SOURCE_PAGE_REQUEST_HEADERS.get(source, {}))
    return headers


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


def append_rejected_sample(
    samples: list[RejectedNewsSample],
    *,
    title: str,
    source: str,
    url: str | None,
    rejection_reason: str,
) -> None:
    if len(samples) >= MAX_REJECTED_SAMPLES:
        return

    normalized_title = normalize_whitespace(title)
    if not normalized_title:
        return

    samples.append(
        RejectedNewsSample(
            title=normalized_title,
            source=source,
            url=url,
            rejection_reason=rejection_reason,
        )
    )


def fetch_url(url: str, *, source: str | None = None, is_feed: bool = False) -> str:
    request = Request(url, headers=build_request_headers(source=source, is_feed=is_feed))
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
) -> tuple[list[NewsArticle], PageFetchMetrics]:
    articles: list[NewsArticle] = []
    page_fetch_success_count = 0
    page_fetch_forbidden_count = 0
    page_fetch_error_count = 0
    for candidate in candidates:
        base_content = normalize_whitespace(f"{candidate.title}. {candidate.summary}")
        content = base_content
        topic_label = candidate.topic_label

        if fetch_pages:
            try:
                page_text = extract_article_text(fetch_url(candidate.url, source=candidate.source))
                if page_text:
                    page_fetch_success_count += 1
            except HTTPError as exc:
                if exc.code == 403:
                    page_fetch_forbidden_count += 1
                    if logger:
                        logger.warning(
                            "Article fetch forbidden | source=%s | url=%s | error=%s",
                            candidate.source,
                            candidate.url,
                            exc,
                        )
                else:
                    page_fetch_error_count += 1
                    if logger:
                        logger.warning(
                            "Article fetch failed | source=%s | url=%s | error=%s",
                            candidate.source,
                            candidate.url,
                            exc,
                        )
                page_text = ""
            except (URLError, TimeoutError, OSError, ValueError) as exc:
                page_fetch_error_count += 1
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
                if topic_label is None:
                    topic_label = classify_macro_topic(content)

        if topic_label is None:
            continue

        articles.append(
            NewsArticle(
                source=candidate.source,
                title=candidate.title,
                url=candidate.url,
                summary=candidate.summary,
                published_at=candidate.published_at,
                topic_label=topic_label,
                content=content,
            )
        )

    return (
        articles,
        PageFetchMetrics(
            success_count=page_fetch_success_count,
            forbidden_count=page_fetch_forbidden_count,
            error_count=page_fetch_error_count,
        ),
    )


def validate_news_articles(
    candidates: list[NewsArticleCandidate],
    *,
    fetch_pages: bool,
    logger: logging.Logger | None = None,
) -> tuple[list[NewsArticle], NewsQualityReport]:
    enriched, page_fetch_metrics = enrich_candidates_with_page_text(
        candidates,
        fetch_pages=fetch_pages,
        logger=logger,
    )
    accepted: list[NewsArticle] = []
    seen_urls: set[str] = set()
    duplicate_url_count = 0
    short_content_count = 0
    topic_coverage: dict[str, int] = {}
    rejected_samples: list[RejectedNewsSample] = []
    accepted_urls = {article.url for article in enriched}

    for candidate in candidates:
        if candidate.topic_label is None and candidate.url not in accepted_urls:
            append_rejected_sample(
                rejected_samples,
                title=candidate.title,
                source=candidate.source,
                url=candidate.url or None,
                rejection_reason="missing_topic_label",
            )

    for article in enriched:
        if article.url in seen_urls:
            duplicate_url_count += 1
            append_rejected_sample(
                rejected_samples,
                title=article.title,
                source=article.source,
                url=article.url,
                rejection_reason="duplicate_url",
            )
            continue
        seen_urls.add(article.url)

        if len(article.content) < MIN_CONTENT_LENGTH:
            short_content_count += 1
            append_rejected_sample(
                rejected_samples,
                title=article.title,
                source=article.source,
                url=article.url,
                rejection_reason="short_content",
            )
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
        page_fetch_success_count=page_fetch_metrics.success_count,
        page_fetch_forbidden_count=page_fetch_metrics.forbidden_count,
        page_fetch_error_count=page_fetch_metrics.error_count,
        topic_coverage=topic_coverage,
        rejected_samples=[asdict(sample) for sample in rejected_samples],
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
        candidates = parse_feed_candidates(
            source,
            fetch_url(source.feed_url, source=source.source, is_feed=True),
        )[:limit]
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
