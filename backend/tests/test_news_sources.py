from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.db.base import Base
from app.services.news_sources import (
    NewsSource,
    classify_macro_topic,
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

    def fake_fetch_url(url: str) -> str:
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
    assert raw_count == 1
    assert run_count == 2
