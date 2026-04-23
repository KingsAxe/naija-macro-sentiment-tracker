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
    ingested_count: int = 0
    skipped_count: int = 0
