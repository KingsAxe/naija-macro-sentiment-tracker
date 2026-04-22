from sqlalchemy import select

from fastapi import APIRouter

from app.api.deps import DbSession
from app.models import AnalyzedSentiment, RawText
from app.schemas.sentiment import FeedItem, FeedResponse

router = APIRouter()


@router.get("/feed", response_model=FeedResponse)
def get_feed(session: DbSession) -> FeedResponse:
    rows = session.execute(
        select(
            RawText.id,
            RawText.source,
            RawText.content,
            RawText.published_at,
            AnalyzedSentiment.overall_sentiment,
        )
        .outerjoin(AnalyzedSentiment, AnalyzedSentiment.raw_text_id == RawText.id)
        .order_by(RawText.published_at.desc().nullslast(), RawText.created_at.desc())
        .limit(25)
    ).all()

    items = [
        FeedItem(
            id=row.id,
            source=row.source,
            content=row.content,
            published_at=row.published_at,
            overall_sentiment=row.overall_sentiment,
        )
        for row in rows
    ]
    return FeedResponse(items=items)
