from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Keep local boot simple until Alembic-managed database setup is fully wired in.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API for ingesting and analyzing macroeconomic sentiment about Nigeria.",
    lifespan=lifespan,
)


app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "environment": settings.app_env,
        "status": "ok",
    }
