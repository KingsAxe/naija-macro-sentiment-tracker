from fastapi import APIRouter

from app.api.deps import DbSession
from app.schemas.sentiment import IngestTriggerResponse
from app.services.ingestion import trigger_ingestion

router = APIRouter()


@router.post("/trigger", response_model=IngestTriggerResponse)
def trigger_ingestion_route(session: DbSession) -> IngestTriggerResponse:
    return trigger_ingestion(session)
