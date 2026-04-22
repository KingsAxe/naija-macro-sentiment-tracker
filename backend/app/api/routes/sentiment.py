from sqlalchemy import case, func, select

from fastapi import APIRouter

from app.api.deps import DbSession
from app.models import AnalyzedSentiment, OpinionTarget
from app.schemas.sentiment import SentimentSummary, TargetSentiment

router = APIRouter()


@router.get("/summary", response_model=SentimentSummary)
def get_summary(session: DbSession) -> SentimentSummary:
    sentiment_counts = session.execute(
        select(
            func.count(AnalyzedSentiment.id),
            func.sum(case((AnalyzedSentiment.overall_sentiment == "positive", 1), else_=0)),
            func.sum(case((AnalyzedSentiment.overall_sentiment == "neutral", 1), else_=0)),
            func.sum(case((AnalyzedSentiment.overall_sentiment == "negative", 1), else_=0)),
        )
    ).one()

    total, positive, neutral, negative = sentiment_counts
    return SentimentSummary(
        total_documents=total or 0,
        positive=positive or 0,
        neutral=neutral or 0,
        negative=negative or 0,
    )


@router.get("/targets", response_model=list[TargetSentiment])
def get_targets(session: DbSession) -> list[TargetSentiment]:
    rows = session.execute(
        select(
            OpinionTarget.target_name,
            func.count(OpinionTarget.id).label("mentions"),
            func.sum(case((OpinionTarget.target_sentiment == "positive", 1), else_=0)).label(
                "positive_mentions"
            ),
            func.sum(case((OpinionTarget.target_sentiment == "neutral", 1), else_=0)).label(
                "neutral_mentions"
            ),
            func.sum(case((OpinionTarget.target_sentiment == "negative", 1), else_=0)).label(
                "negative_mentions"
            ),
        )
        .group_by(OpinionTarget.target_name)
        .order_by(func.count(OpinionTarget.id).desc(), OpinionTarget.target_name.asc())
        .limit(20)
    ).all()

    return [
        TargetSentiment(
            target_name=row.target_name,
            mentions=row.mentions or 0,
            positive_mentions=row.positive_mentions or 0,
            neutral_mentions=row.neutral_mentions or 0,
            negative_mentions=row.negative_mentions or 0,
        )
        for row in rows
    ]
