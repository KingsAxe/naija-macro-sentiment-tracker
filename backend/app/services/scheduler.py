from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.services.analysis import analyze_pending_sentiments, azure_language_is_configured
from app.services.ingestion import ingest_file_to_database
from app.services.news_sources import ingest_news_sources

logger = logging.getLogger("app.scheduler")
settings = get_settings()


@dataclass(slots=True)
class SchedulerSnapshot:
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


def compute_next_run_at(now: datetime, daily_hour: int) -> datetime:
    candidate = now.replace(hour=daily_hour, minute=0, second=0, microsecond=0)
    if candidate <= now:
        candidate = candidate + timedelta(days=1)
    return candidate


class IngestionScheduler:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory
        self._enabled = settings.scheduler_enabled
        self._daily_hour = settings.scheduler_daily_hour
        self._include_news = settings.scheduler_include_news
        self._skip_news_pages = settings.scheduler_skip_news_pages
        self._news_limit = settings.scheduler_news_limit
        self._running = False
        self._next_run_at: datetime | None = None
        self._last_started_at: datetime | None = None
        self._last_completed_at: datetime | None = None
        self._last_status: str | None = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._wake_event = threading.Event()
        self._lock = threading.Lock()

    def start(self) -> None:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._stop_event.clear()
            self._wake_event.clear()
            self._thread = threading.Thread(target=self._run_loop, name="ingestion-scheduler", daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._wake_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
        with self._lock:
            self._running = False
            self._next_run_at = None

    def set_enabled(self, enabled: bool) -> SchedulerSnapshot:
        with self._lock:
            self._enabled = enabled
            if enabled:
                self._next_run_at = compute_next_run_at(datetime.now(), self._daily_hour)
            else:
                self._next_run_at = None
        self._wake_event.set()
        return self.snapshot()

    def snapshot(self) -> SchedulerSnapshot:
        with self._lock:
            return SchedulerSnapshot(
                enabled=self._enabled,
                running=self._running,
                daily_hour=self._daily_hour,
                next_run_at=self._next_run_at,
                last_started_at=self._last_started_at,
                last_completed_at=self._last_completed_at,
                last_status=self._last_status,
                include_news=self._include_news,
                skip_news_pages=self._skip_news_pages,
                news_limit=self._news_limit,
            )

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            with self._lock:
                enabled = self._enabled

            if not enabled:
                self._wake_event.wait(timeout=5)
                self._wake_event.clear()
                continue

            now = datetime.now()
            next_run_at = compute_next_run_at(now, self._daily_hour)
            with self._lock:
                self._next_run_at = next_run_at

            wait_seconds = max((next_run_at - now).total_seconds(), 1)
            was_woken = self._wake_event.wait(timeout=wait_seconds)
            self._wake_event.clear()
            if was_woken or self._stop_event.is_set():
                continue

            self._execute_run()

    def _execute_run(self) -> None:
        with self._lock:
            self._running = True
            self._last_started_at = datetime.now()
            self._last_status = "running"

        session = self._session_factory()
        try:
            ingest_file_to_database(session=session, file_path=settings.csv_source_path, logger=logger)
            if self._include_news:
                ingest_news_sources(
                    session=session,
                    limit_per_source=self._news_limit,
                    fetch_pages=not self._skip_news_pages,
                    logger=logger,
                )
            if azure_language_is_configured():
                analyze_pending_sentiments(session=session, logger=logger)
            with self._lock:
                self._last_status = "completed"
        except Exception:
            logger.exception("Scheduled ingestion run failed")
            with self._lock:
                self._last_status = "failed"
        finally:
            session.close()
            with self._lock:
                self._running = False
                self._last_completed_at = datetime.now()

ingestion_scheduler = IngestionScheduler(SessionLocal)
