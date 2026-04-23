from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.db.base import Base
from app.services.news_sources import (
    NewsSource,
    classify_macro_topic,
    extract_article_text,
    ingest_news_source,
    parse_feed_items,
)


def test_parse_feed_items_keeps_macro_relevant_articles() -> None:
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

    articles = parse_feed_items(NewsSource(source="punch", feed_url="https://example.com"), feed_xml)

    assert len(articles) == 1
    assert articles[0].source == "punch"
    assert articles[0].topic_label == "FX Rate"
    assert articles[0].published_at is not None


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
    assert raw_count == 1
    assert run_count == 2
