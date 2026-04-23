from dataclasses import asdict

from sqlalchemy import select

from app.api.deps import DbSession
from app.models import IngestionRun
from app.schemas.sentiment import (
    IngestionRunSummary,
    IngestTriggerResponse,
    SchedulerStatusResponse,
    SchedulerToggleRequest,
)
from app.services.ingestion import trigger_ingestion
from app.services.scheduler import ingestion_scheduler

from fastapi import APIRouter

router = APIRouter()


@router.post("/trigger", response_model=IngestTriggerResponse)
def trigger_ingestion_route(session: DbSession) -> IngestTriggerResponse:
    return trigger_ingestion(session)


@router.get("/runs", response_model=list[IngestionRunSummary])
def list_recent_ingestion_runs(session: DbSession) -> list[IngestionRunSummary]:
    rows = session.scalars(select(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(10)).all()
    return [
        IngestionRunSummary(
            id=row.id,
            source_type=row.source_type,
            source_name=row.source_name,
            source_file=row.source_file,
            status=row.status,
            fetched_count=row.fetched_count,
            inserted_count=row.inserted_count,
            skipped_count=row.skipped_count,
            duplicate_count=row.duplicate_count,
            rejected_count=row.rejected_count,
            qa_summary=row.qa_summary,
            error_message=row.error_message,
            started_at=row.started_at,
            completed_at=row.completed_at,
        )
        for row in rows
    ]


@router.get("/scheduler", response_model=SchedulerStatusResponse)
def get_scheduler_status() -> SchedulerStatusResponse:
    snapshot = ingestion_scheduler.snapshot()
    return SchedulerStatusResponse(**asdict(snapshot))


@router.post("/scheduler", response_model=SchedulerStatusResponse)
def toggle_scheduler(payload: SchedulerToggleRequest) -> SchedulerStatusResponse:
    snapshot = ingestion_scheduler.set_enabled(payload.enabled)
    return SchedulerStatusResponse(**asdict(snapshot))
