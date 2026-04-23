from datetime import datetime

from pydantic import BaseModel


class SentimentSummary(BaseModel):
    total_documents: int
    positive: int
    neutral: int
    negative: int


class TargetSentiment(BaseModel):
    target_name: str
    mentions: int
    positive_mentions: int
    neutral_mentions: int
    negative_mentions: int


class AssessmentSentiment(BaseModel):
    assessment_text: str
    mentions: int
    positive_mentions: int
    neutral_mentions: int
    negative_mentions: int


class FeedItem(BaseModel):
    id: int
    source: str
    topic_label: str | None
    content: str
    published_at: datetime | None
    overall_sentiment: str | None


class FeedResponse(BaseModel):
    items: list[FeedItem]


class IngestTriggerResponse(BaseModel):
    status: str
    detail: str
    run_id: int | None = None
    source_file: str | None = None
    source_name: str | None = None
    fetched_count: int = 0
    ingested_count: int = 0
    skipped_count: int = 0
    duplicate_count: int = 0
    rejected_count: int = 0
    qa_summary: str | None = None


class IngestionRunSummary(BaseModel):
    id: int
    source_type: str
    source_name: str | None
    source_file: str | None
    status: str
    fetched_count: int
    inserted_count: int
    skipped_count: int
    duplicate_count: int
    rejected_count: int
    qa_summary: str | None
    error_message: str | None
    started_at: datetime
    completed_at: datetime | None


class SchedulerStatusResponse(BaseModel):
    enabled: bool
    running: bool
    daily_hour: int
    next_run_at: datetime | None
    last_started_at: datetime | None
    last_completed_at: datetime | None
    last_status: str | None
    include_news: bool
    skip_news_pages: bool
    news_limit: int


class SchedulerToggleRequest(BaseModel):
    enabled: bool
