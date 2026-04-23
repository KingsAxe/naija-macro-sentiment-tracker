from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_db_session
from app.db.base import Base
from app.main import app
from app.services.ingestion import prepare_clean_records


def build_test_client(tmp_path: Path) -> TestClient:
    database_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)

    def override_get_db_session():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db_session] = override_get_db_session
    client = TestClient(app)
    client._test_engine = engine  # type: ignore[attr-defined]
    return client


def test_healthcheck_and_frontdoor_routes(tmp_path: Path) -> None:
    client = build_test_client(tmp_path)

    root_response = client.get("/")
    health_response = client.get("/api/health")
    summary_response = client.get("/api/sentiment/summary")
    targets_response = client.get("/api/sentiment/targets")
    feed_response = client.get("/api/feed")
    scheduler_response = client.get("/api/ingest/scheduler")
    runs_response = client.get("/api/ingest/runs")

    assert root_response.status_code == 200
    assert health_response.status_code == 200
    assert summary_response.status_code == 200
    assert targets_response.status_code == 200
    assert feed_response.status_code == 200
    assert scheduler_response.status_code == 200
    assert runs_response.status_code == 200
    assert summary_response.json() == {
        "total_documents": 0,
        "positive": 0,
        "neutral": 0,
        "negative": 0,
    }
    assert targets_response.json() == []
    assert feed_response.json() == {"items": []}
    assert scheduler_response.json()["enabled"] is False
    assert runs_response.json() == []


def test_manual_ingestion_writes_raw_text_records(tmp_path: Path) -> None:
    client = build_test_client(tmp_path)
    engine = client._test_engine  # type: ignore[attr-defined]
    cleaned, _ = prepare_clean_records("data/raw_macro_data.csv")

    response = client.post("/api/ingest/trigger")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["run_id"] is not None
    assert payload["source_name"] == "x"
    assert payload["fetched_count"] == len(cleaned)
    assert payload["ingested_count"] == len(cleaned)
    assert payload["skipped_count"] == 0
    assert payload["duplicate_count"] == 0
    assert payload["rejected_count"] == 0
    assert payload["qa_summary"] is not None

    with Session(engine) as session:
        row_count = session.execute(text("select count(*) from raw_texts")).scalar_one()
        run_count = session.execute(text("select count(*) from ingestion_runs")).scalar_one()

    assert row_count == len(cleaned)
    assert run_count == 1


def test_manual_ingestion_reports_duplicate_records(tmp_path: Path) -> None:
    client = build_test_client(tmp_path)
    cleaned, _ = prepare_clean_records("data/raw_macro_data.csv")

    first_response = client.post("/api/ingest/trigger")
    second_response = client.post("/api/ingest/trigger")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    payload = second_response.json()
    assert payload["status"] == "completed"
    assert payload["ingested_count"] == 0
    assert payload["fetched_count"] == len(cleaned)
    assert payload["skipped_count"] == len(cleaned)
    assert payload["duplicate_count"] == len(cleaned)


def test_scheduler_toggle_endpoint(tmp_path: Path) -> None:
    client = build_test_client(tmp_path)

    enable_response = client.post("/api/ingest/scheduler", json={"enabled": True})
    disable_response = client.post("/api/ingest/scheduler", json={"enabled": False})

    assert enable_response.status_code == 200
    assert enable_response.json()["enabled"] is True
    assert enable_response.json()["next_run_at"] is not None
    assert disable_response.status_code == 200
    assert disable_response.json()["enabled"] is False
    assert disable_response.json()["next_run_at"] is None


def test_schema_metadata_matches_initial_tables(tmp_path: Path) -> None:
    database_path = tmp_path / "schema.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)

    assert set(inspector.get_table_names()) == {
        "analyzed_sentiments",
        "ingestion_runs",
        "opinion_assessments",
        "opinion_targets",
        "raw_texts",
    }
