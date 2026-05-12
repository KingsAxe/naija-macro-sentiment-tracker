from urllib.error import HTTPError, URLError
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import pytest
import json

from app.db.base import Base
from app.services.news_sources import (
    build_request_headers,
    NewsSource,
    classify_macro_topic,
    prepare_analysis_content,
    extract_article_text,
    ingest_news_source,
    parse_feed_candidates,
    validate_news_articles,
)


def test_parse_feed_candidates_keeps_feed_items_and_marks_topics() -> None:
    feed_xml = """<?xml version="1.0"?>
    <rss><channel>
      <item>
        <title>CBN warns banks as naira pressure rises</title>
        <link>https://example.com/fx-story</link>
        <description>Naira and dollar liquidity remain in focus.</description>
        <pubDate>Thu, 23 Apr 2026 10:00:00 +0100</pubDate>
      </item>
      <item>
        <title>Celebrity wedding draws crowd</title>
        <link>https://example.com/entertainment</link>
        <description>Guests arrived early.</description>
      </item>
    </channel></rss>
    """

    articles = parse_feed_candidates(
        NewsSource(source="punch", feed_url="https://example.com"),
        feed_xml,
    )

    assert len(articles) == 2
    assert articles[0].source == "punch"
    assert articles[0].topic_label == "FX Rate"
    assert articles[0].published_at is not None
    assert articles[1].topic_label is None


def test_article_extraction_and_topic_classification() -> None:
    html = """
    <html><body>
      <p>Short.</p>
      <p>Petrol prices moved again after fuel marketers reviewed landing costs.</p>
    </body></html>
    """

    text = extract_article_text(html)

    assert "Petrol prices" in text
    assert classify_macro_topic(text) == "Fuel Price"


def test_build_request_headers_uses_browser_like_defaults_and_source_overrides() -> None:
    headers = build_request_headers(source="vanguard")

    assert "Mozilla/5.0" in headers["User-Agent"]
    assert headers["Accept-Language"] == "en-US,en;q=0.9"
    assert headers["Referer"] == "https://www.vanguardngr.com/category/business/"


def test_build_request_headers_uses_feed_accept_header_for_feed_requests() -> None:
    headers = build_request_headers(source="punch", is_feed=True)

    assert headers["Accept"].startswith("application/rss+xml")


def test_prepare_analysis_content_deduplicates_and_filters_low_signal_paragraphs() -> None:
    content = prepare_analysis_content(
        title="Fuel prices jump again",
        summary="Fuel prices rose sharply after depot adjustments.",
        article_paragraphs=[
            "ADVERTISEMENT",
            "Fuel prices rose sharply after depot adjustments.",
            "Independent marketers said logistics costs remain elevated across major depots.",
            "Read also: Market roundup",
            "Independent marketers said logistics costs remain elevated across major depots.",
        ],
    )

    assert "ADVERTISEMENT" not in content
    assert "Read also" not in content
    assert content.count("Fuel prices rose sharply after depot adjustments.") == 1
    assert "Independent marketers said logistics costs remain elevated across major depots." in content


@pytest.mark.parametrize(
    ("text", "expected_topic"),
    [
        ("MPC members signalled tighter monetary policy after the meeting.", "Monetary Policy"),
        ("Banks raised lending rates as borrowing costs climbed for manufacturers.", "Interest Rates"),
        ("Consumer prices worsened the cost of living for many households.", "Cost of Living"),
        ("Electricity tariff changes are hitting the power sector.", "Power/Energy"),
        ("Import duty changes raised port charges for traders.", "Trade/Imports"),
        ("Credit to private sector slowed as bank lending conditions tightened.", "Banking/Credit"),
        ("Tax revenue shortfalls widened the budget deficit.", "Budget/Fiscal Policy"),
        ("Haulage and logistics costs increased across key trade routes.", "Transport/Logistics"),
        ("Workers union leaders renewed calls over unemployment and wages.", "Employment/Labour"),
        ("Private sector confidence dipped as PMI data weakened.", "Business Confidence/Private Sector"),
    ],
)
def test_classify_macro_topic_supports_expanded_taxonomy(text: str, expected_topic: str) -> None:
    assert classify_macro_topic(text) == expected_topic


def test_validate_news_articles_reports_rejections() -> None:
    candidates = [
        NewsSource(source="vanguard", feed_url="https://example.com/feed"),
    ]
    feed_xml = """<?xml version="1.0"?>
    <rss><channel>
      <item>
        <title>CBN says naira pressure is easing</title>
        <link>https://example.com/a</link>
        <description>Naira liquidity is improving in the official market.</description>
      </item>
      <item>
        <title>CBN says naira pressure is easing</title>
        <link>https://example.com/a</link>
        <description>Naira liquidity is improving in the official market.</description>
      </item>
      <item>
        <title>Music concert sells out</title>
        <link>https://example.com/b</link>
        <description>Fans arrived early.</description>
      </item>
    </channel></rss>
    """

    parsed = parse_feed_candidates(candidates[0], feed_xml)
    accepted, report = validate_news_articles(parsed, fetch_pages=False)

    assert len(accepted) == 1
    assert report.fetched_count == 3
    assert report.missing_topic_count == 1
    assert report.duplicate_url_count == 1
    assert report.accepted_count == 1
    assert report.rejected_samples == [
        {
            "title": "Music concert sells out",
            "source": "vanguard",
            "url": "https://example.com/b",
            "rejection_reason": "missing_topic_label",
        },
        {
            "title": "CBN says naira pressure is easing",
            "source": "vanguard",
            "url": "https://example.com/a",
            "rejection_reason": "duplicate_url",
        },
    ]


def test_validate_news_articles_reclassifies_unmatched_item_with_page_text(monkeypatch) -> None:
    candidates = [
        NewsSource(source="vanguard", feed_url="https://example.com/feed"),
    ]
    feed_xml = """<?xml version="1.0"?>
    <rss><channel>
      <item>
        <title>Business desk update</title>
        <link>https://example.com/energy-story</link>
        <description>Markets are watching incoming data.</description>
      </item>
    </channel></rss>
    """

    def fake_fetch_url(url: str, *, source: str | None = None, is_feed: bool = False) -> str:
        assert url == "https://example.com/energy-story"
        assert source == "vanguard"
        assert is_feed is False
        return """
        <html><body>
          <p>Electricity tariff changes continue to pressure the power sector and energy-intensive factories.</p>
        </body></html>
        """

    monkeypatch.setattr("app.services.news_sources.fetch_url", fake_fetch_url)

    parsed = parse_feed_candidates(candidates[0], feed_xml)
    accepted, report = validate_news_articles(parsed, fetch_pages=True)

    assert len(accepted) == 1
    assert accepted[0].topic_label == "Power/Energy"
    assert report.missing_topic_count == 1
    assert report.accepted_count == 1
    assert report.page_fetch_success_count == 1
    assert report.page_fetch_forbidden_count == 0
    assert report.page_fetch_error_count == 0
    assert report.rejected_samples == []
    assert "Markets are watching incoming data." in accepted[0].content


def test_validate_news_articles_preserves_safe_fallback_when_page_fetch_fails(monkeypatch) -> None:
    candidates = [
        NewsSource(source="punch", feed_url="https://example.com/feed"),
    ]
    feed_xml = """<?xml version="1.0"?>
    <rss><channel>
      <item>
        <title>Business desk update</title>
        <link>https://example.com/unmatched-story</link>
        <description>Markets are watching incoming data.</description>
      </item>
    </channel></rss>
    """

    def failing_fetch_url(url: str, *, source: str | None = None, is_feed: bool = False) -> str:
        raise URLError("network unavailable")

    monkeypatch.setattr("app.services.news_sources.fetch_url", failing_fetch_url)

    parsed = parse_feed_candidates(candidates[0], feed_xml)
    accepted, report = validate_news_articles(parsed, fetch_pages=True)

    assert accepted == []
    assert report.missing_topic_count == 1
    assert report.page_fetch_success_count == 0
    assert report.page_fetch_forbidden_count == 0
    assert report.page_fetch_error_count == 1
    assert report.rejected_samples == [
        {
            "title": "Business desk update",
            "source": "punch",
            "url": "https://example.com/unmatched-story",
            "rejection_reason": "missing_topic_label",
        }
    ]


def test_validate_news_articles_records_forbidden_fetch_outcome_and_preserves_fallback(monkeypatch) -> None:
    candidates = [
        NewsSource(source="vanguard", feed_url="https://example.com/feed"),
    ]
    feed_xml = """<?xml version="1.0"?>
    <rss><channel>
      <item>
        <title>Business desk update</title>
        <link>https://example.com/blocked-story</link>
        <description>Markets are watching incoming data.</description>
      </item>
    </channel></rss>
    """

    def forbidden_fetch_url(url: str, *, source: str | None = None, is_feed: bool = False) -> str:
        raise HTTPError(url, 403, "Forbidden", hdrs=None, fp=None)

    monkeypatch.setattr("app.services.news_sources.fetch_url", forbidden_fetch_url)

    parsed = parse_feed_candidates(candidates[0], feed_xml)
    accepted, report = validate_news_articles(parsed, fetch_pages=True)

    assert accepted == []
    assert report.missing_topic_count == 1
    assert report.page_fetch_success_count == 0
    assert report.page_fetch_forbidden_count == 1
    assert report.page_fetch_error_count == 0
    assert report.rejected_samples == [
        {
            "title": "Business desk update",
            "source": "vanguard",
            "url": "https://example.com/blocked-story",
            "rejection_reason": "missing_topic_label",
        }
    ]


def test_validate_news_articles_caps_rejected_samples() -> None:
    candidates = [
        NewsSource(source="punch", feed_url="https://example.com/feed"),
    ]
    feed_xml = """<?xml version="1.0"?>
    <rss><channel>
      <item><title>Entertainment headline 1</title><link>https://example.com/1</link><description>Guests arrived early.</description></item>
      <item><title>Entertainment headline 2</title><link>https://example.com/2</link><description>Guests arrived early.</description></item>
      <item><title>Entertainment headline 3</title><link>https://example.com/3</link><description>Guests arrived early.</description></item>
      <item><title>Entertainment headline 4</title><link>https://example.com/4</link><description>Guests arrived early.</description></item>
      <item><title>Entertainment headline 5</title><link>https://example.com/5</link><description>Guests arrived early.</description></item>
      <item><title>Entertainment headline 6</title><link>https://example.com/6</link><description>Guests arrived early.</description></item>
      <item><title>Entertainment headline 7</title><link>https://example.com/7</link><description>Guests arrived early.</description></item>
    </channel></rss>
    """

    parsed = parse_feed_candidates(candidates[0], feed_xml)
    accepted, report = validate_news_articles(parsed, fetch_pages=False)

    assert accepted == []
    assert report.missing_topic_count == 7
    assert len(report.rejected_samples) == 5
    assert all(sample["rejection_reason"] == "missing_topic_label" for sample in report.rejected_samples)


def test_news_source_ingestion_records_run_and_duplicates(monkeypatch) -> None:
    feed_xml = """<?xml version="1.0"?>
    <rss><channel>
      <item>
        <title>Food inflation puts pressure on households</title>
        <link>https://example.com/food-story</link>
        <description>Rice and food prices remain elevated.</description>
        <pubDate>Thu, 23 Apr 2026 10:00:00 +0100</pubDate>
      </item>
    </channel></rss>
    """

    def fake_fetch_url(url: str, *, source: str | None = None, is_feed: bool = False) -> str:
        return feed_xml

    monkeypatch.setattr("app.services.news_sources.fetch_url", fake_fetch_url)

    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    source = NewsSource(source="vanguard", feed_url="https://example.com/feed")

    with Session(engine) as session:
        first_result = ingest_news_source(session, source, fetch_pages=False)
        second_result = ingest_news_source(session, source, fetch_pages=False)
        raw_count = session.execute(text("select count(*) from raw_texts")).scalar_one()
        run_count = session.execute(text("select count(*) from ingestion_runs")).scalar_one()

    assert first_result.ingested_count == 1
    assert second_result.ingested_count == 0
    assert second_result.duplicate_count == 1
    assert first_result.qa_summary is not None
    qa_summary = json.loads(first_result.qa_summary)
    assert qa_summary["rejected_samples"] == []
    assert qa_summary["page_fetch_forbidden_count"] == 0
    assert raw_count == 1
    assert run_count == 2


def test_news_source_ingestion_records_rejected_samples(monkeypatch) -> None:
    feed_xml = """<?xml version="1.0"?>
    <rss><channel>
      <item>
        <title>Food inflation puts pressure on households</title>
        <link>https://example.com/food-story</link>
        <description>Rice and food prices remain elevated.</description>
      </item>
      <item>
        <title>Entertainment event thrills fans</title>
        <link>https://example.com/entertainment-story</link>
        <description>Guests arrived early.</description>
      </item>
    </channel></rss>
    """

    def fake_fetch_url(url: str, *, source: str | None = None, is_feed: bool = False) -> str:
        return feed_xml

    monkeypatch.setattr("app.services.news_sources.fetch_url", fake_fetch_url)

    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    source = NewsSource(source="punch", feed_url="https://example.com/feed")

    with Session(engine) as session:
        result = ingest_news_source(session, source, fetch_pages=False)

    qa_summary = json.loads(result.qa_summary or "{}")

    assert result.rejected_count == 1
    assert qa_summary["missing_topic_count"] == 1
    assert qa_summary["rejected_samples"] == [
        {
            "title": "Entertainment event thrills fans",
            "source": "punch",
            "url": "https://example.com/entertainment-story",
            "rejection_reason": "missing_topic_label",
        }
    ]
