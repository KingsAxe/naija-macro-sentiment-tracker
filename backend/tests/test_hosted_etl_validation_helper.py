from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def load_helper_module():
    repo_root = Path(__file__).resolve().parents[2]
    module_path = repo_root / "scripts" / "hosted_etl_validation.py"
    spec = importlib.util.spec_from_file_location("hosted_etl_validation", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_parse_qa_summary_handles_invalid_json() -> None:
    module = load_helper_module()

    assert module.parse_qa_summary(None) == {}
    assert module.parse_qa_summary("not-json") == {}


def test_build_validation_report_summarizes_latest_source_runs() -> None:
    module = load_helper_module()

    results = {
        "health": module.FetchResult(ok=True, status_code=200, payload={"status": "ok"}, error=None),
        "summary": module.FetchResult(
            ok=True,
            status_code=200,
            payload={"total_documents": 12, "positive": 4, "neutral": 5, "negative": 3},
            error=None,
        ),
        "targets": module.FetchResult(ok=True, status_code=200, payload=[{"target_name": "naira"}], error=None),
        "assessments": module.FetchResult(ok=True, status_code=200, payload=[{"assessment_text": "volatile"}], error=None),
        "feed": module.FetchResult(ok=True, status_code=200, payload={"items": [{"id": 1}, {"id": 2}]}, error=None),
        "runs": module.FetchResult(
            ok=True,
            status_code=200,
            payload=[
                {
                    "id": 10,
                    "source_name": "punch",
                    "source_type": "news_feed",
                    "status": "completed",
                    "fetched_count": 20,
                    "inserted_count": 7,
                    "duplicate_count": 0,
                    "rejected_count": 13,
                    "qa_summary": '{"page_fetch_success_count": 4, "page_fetch_forbidden_count": 0, "page_fetch_error_count": 1, "missing_topic_count": 13}',
                    "started_at": "2026-05-10T08:00:00Z",
                    "completed_at": "2026-05-10T08:10:00Z",
                },
                {
                    "id": 11,
                    "source_name": "vanguard",
                    "source_type": "news_feed",
                    "status": "completed",
                    "fetched_count": 20,
                    "inserted_count": 3,
                    "duplicate_count": 0,
                    "rejected_count": 17,
                    "qa_summary": '{"page_fetch_success_count": 1, "page_fetch_forbidden_count": 9, "page_fetch_error_count": 2, "missing_topic_count": 17}',
                    "started_at": "2026-05-10T08:00:00Z",
                    "completed_at": "2026-05-10T08:10:00Z",
                },
            ],
            error=None,
        ),
    }

    report = module.build_validation_report("https://example.com/api", results)

    assert report["health"]["ok"] is True
    assert report["analysis"]["analyzed_documents"] == 12
    assert report["analysis"]["targets_count"] == 1
    assert report["analysis"]["assessments_count"] == 1
    assert report["feed"]["items_count"] == 2
    assert report["latest_runs"]["vanguard"]["page_fetch_forbidden"] == 9
    assert report["latest_runs"]["punch"]["inserted"] == 7


def test_format_report_mentions_source_fetch_outcomes() -> None:
    module = load_helper_module()

    report = {
        "api_base_url": "https://example.com/api",
        "health": {"ok": True, "status_code": 200, "payload": {"status": "ok"}, "error": None},
        "analysis": {
            "analyzed_documents": 40,
            "positive": 11,
            "neutral": 18,
            "negative": 11,
            "targets_count": 2,
            "assessments_count": 3,
        },
        "feed": {"items_count": 25},
        "latest_runs": {
            "vanguard": {
                "status": "completed",
                "fetched": 20,
                "inserted": 3,
                "rejected": 17,
                "duplicates": 0,
                "page_fetch_success": 1,
                "page_fetch_forbidden": 9,
                "page_fetch_error": 2,
                "missing_topic": 17,
            },
            "punch": None,
        },
        "endpoint_status": {
            "health": {"ok": True, "status_code": 200, "error": None},
        },
    }

    output = module.format_report(report)

    assert "Hosted ETL validation summary" in output
    assert "Vanguard: status=completed fetched=20 inserted=3 rejected=17 duplicates=0" in output
    assert "fetch outcomes: success=1 forbidden=9 errors=2 missing_topic=17" in output
    assert "Punch: no recent run found" in output
