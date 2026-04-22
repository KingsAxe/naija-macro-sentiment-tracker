from fastapi import APIRouter

from app.api.routes import feed, health, ingestion, sentiment

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(sentiment.router, prefix="/sentiment", tags=["sentiment"])
api_router.include_router(feed.router, tags=["feed"])
api_router.include_router(ingestion.router, prefix="/ingest", tags=["ingestion"])
