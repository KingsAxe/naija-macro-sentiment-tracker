from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Protocol

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import AnalyzedSentiment, OpinionAssessment, OpinionTarget, RawText

settings = get_settings()


class SentimentClient(Protocol):
    def analyze_sentiment(self, documents: list[dict[str, str]], *, show_opinion_mining: bool): ...


@dataclass(slots=True)
class AnalysisRunResult:
    analyzed_count: int
    target_count: int
    assessment_count: int
    skipped_count: int


def azure_language_is_configured() -> bool:
    return bool(settings.azure_language_endpoint and settings.azure_language_key)


def build_text_analytics_client() -> TextAnalyticsClient:
    if not azure_language_is_configured():
        raise RuntimeError("Azure AI Language credentials are not configured.")

    return TextAnalyticsClient(
        endpoint=settings.azure_language_endpoint,
        credential=AzureKeyCredential(settings.azure_language_key),
    )


def fetch_pending_raw_texts(session: Session, limit: int | None = None) -> list[RawText]:
    query = (
        select(RawText)
        .outerjoin(AnalyzedSentiment, AnalyzedSentiment.raw_text_id == RawText.id)
        .where(AnalyzedSentiment.id.is_(None))
        .order_by(RawText.id.asc())
    )
    if limit is not None:
        query = query.limit(limit)
    return list(session.scalars(query).all())


def _chunk_documents(items: list[RawText], chunk_size: int) -> list[list[RawText]]:
    return [items[index : index + chunk_size] for index in range(0, len(items), chunk_size)]


def _analyze_batch_with_retry(
    client: SentimentClient,
    documents: list[dict[str, str]],
) -> list[object]:
    last_error: Exception | None = None
    for attempt in range(1, settings.azure_language_retry_attempts + 1):
        try:
            return list(client.analyze_sentiment(documents, show_opinion_mining=True))
        except Exception as exc:  # pragma: no cover
            last_error = exc
            if attempt >= settings.azure_language_retry_attempts:
                break
            time.sleep(settings.azure_language_retry_delay_seconds)

    assert last_error is not None
    raise last_error


def analyze_pending_sentiments(
    session: Session,
    client: SentimentClient | None = None,
    logger: logging.Logger | None = None,
) -> AnalysisRunResult:
    pending = fetch_pending_raw_texts(session)
    if not pending:
        return AnalysisRunResult(
            analyzed_count=0,
            target_count=0,
            assessment_count=0,
            skipped_count=0,
        )

    active_client = client or build_text_analytics_client()
    batches = _chunk_documents(pending, settings.azure_language_batch_size)

    analyzed_count = 0
    target_count = 0
    assessment_count = 0
    skipped_count = 0

    for batch_index, batch in enumerate(batches, start=1):
        documents = [
            {
                "id": str(item.id),
                "text": item.content,
                "language": settings.azure_language_default_language,
            }
            for item in batch
        ]

        if logger:
            logger.info(
                "Submitting Azure sentiment batch %s/%s with %s document(s)",
                batch_index,
                len(batches),
                len(documents),
            )

        results = _analyze_batch_with_retry(active_client, documents)

        for item, result in zip(batch, results, strict=True):
            if getattr(result, "is_error", False):
                skipped_count += 1
                if logger:
                    logger.warning("Azure sentiment skipped raw_text_id=%s because the document errored", item.id)
                continue

            sentiment = AnalyzedSentiment(
                raw_text_id=item.id,
                overall_sentiment=result.sentiment,
                confidence_positive=result.confidence_scores.positive,
                confidence_neutral=result.confidence_scores.neutral,
                confidence_negative=result.confidence_scores.negative,
            )
            session.add(sentiment)
            session.flush()
            analyzed_count += 1

            opinions_added = 0
            assessments_added = 0
            for sentence in getattr(result, "sentences", []):
                for mined_opinion in getattr(sentence, "mined_opinions", []):
                    opinion_target = OpinionTarget(
                        analyzed_sentiment_id=sentiment.id,
                        target_name=mined_opinion.target.text,
                        target_sentiment=mined_opinion.target.sentiment,
                    )
                    session.add(opinion_target)
                    session.flush()
                    opinions_added += 1

                    for assessment in getattr(mined_opinion, "assessments", []):
                        session.add(
                            OpinionAssessment(
                                opinion_target_id=opinion_target.id,
                                assessment_text=assessment.text,
                                assessment_sentiment=assessment.sentiment,
                            )
                        )
                        assessments_added += 1

            target_count += opinions_added
            assessment_count += assessments_added

        session.commit()
        if batch_index < len(batches):
            time.sleep(settings.azure_language_batch_sleep_seconds)

    return AnalysisRunResult(
        analyzed_count=analyzed_count,
        target_count=target_count,
        assessment_count=assessment_count,
        skipped_count=skipped_count,
    )
