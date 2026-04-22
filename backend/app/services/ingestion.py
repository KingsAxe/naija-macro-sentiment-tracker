from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import RawText
from app.schemas.sentiment import IngestTriggerResponse

settings = get_settings()
BACKEND_ROOT = Path(__file__).resolve().parents[2]


def _parse_datetime(value: str) -> datetime | None:
    normalized = value.strip()
    if not normalized:
        return None
    return datetime.fromisoformat(normalized.replace("Z", "+00:00"))


def trigger_ingestion(session: Session) -> IngestTriggerResponse:
    csv_path = Path(settings.csv_source_path)
    if not csv_path.is_absolute():
        csv_path = (BACKEND_ROOT / csv_path).resolve()
    if not csv_path.exists():
        return IngestTriggerResponse(
            status="error",
            detail=f"CSV source not found at {csv_path}.",
        )

    ingested_count = 0
    skipped_count = 0

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            content = (row.get("content") or "").strip()
            source = (row.get("source") or "csv").strip()
            source_url = (row.get("source_url") or "").strip() or None
            published_at = _parse_datetime(row.get("published_at") or "")

            if not content:
                skipped_count += 1
                continue

            existing = session.execute(
                select(RawText.id).where(
                    RawText.source == source,
                    RawText.content == content,
                )
            ).scalar_one_or_none()

            if existing is not None:
                skipped_count += 1
                continue

            session.add(
                RawText(
                    source=source,
                    content=content,
                    source_url=source_url,
                    published_at=published_at,
                )
            )
            ingested_count += 1

    session.commit()

    return IngestTriggerResponse(
        status="completed",
        detail="CSV ingestion finished. Sentiment analysis is not wired yet.",
        ingested_count=ingested_count,
        skipped_count=skipped_count,
    )
