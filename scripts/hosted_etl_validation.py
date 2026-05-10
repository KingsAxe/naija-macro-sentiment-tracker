from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_TIMEOUT_SECONDS = 20
DEFAULT_API_BASE_URL = "http://127.0.0.1:8000/api"
VALIDATION_USER_AGENT = "NaijaMacroSentimentTrackerValidation/0.1"


@dataclass(frozen=True, slots=True)
class FetchResult:
    ok: bool
    status_code: int | None
    payload: Any | None
    error: str | None


def normalize_base_url(value: str) -> str:
    return value.rstrip("/")


def fetch_json(base_url: str, path: str, *, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> FetchResult:
    url = f"{normalize_base_url(base_url)}{path}"
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": VALIDATION_USER_AGENT,
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", None)
            payload = json.loads(response.read().decode("utf-8"))
            return FetchResult(ok=True, status_code=status, payload=payload, error=None)
    except HTTPError as exc:
        detail: str | None = None
        try:
            detail = exc.read().decode("utf-8", errors="replace")
        except Exception:
            detail = None
        return FetchResult(ok=False, status_code=exc.code, payload=None, error=detail or str(exc))
    except (URLError, TimeoutError, ValueError) as exc:
        return FetchResult(ok=False, status_code=None, payload=None, error=str(exc))


def parse_qa_summary(raw_value: str | None) -> dict[str, Any]:
    if not raw_value:
        return {}
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def coerce_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def summarize_run(run: dict[str, Any]) -> dict[str, Any]:
    qa_summary = parse_qa_summary(run.get("qa_summary"))
    return {
        "id": run.get("id"),
        "source_name": run.get("source_name") or "unknown",
        "source_type": run.get("source_type") or "unknown",
        "status": run.get("status") or "unknown",
        "inserted": coerce_int(run.get("inserted_count")),
        "rejected": coerce_int(run.get("rejected_count")),
        "duplicates": coerce_int(run.get("duplicate_count") or run.get("skipped_count")),
        "fetched": coerce_int(run.get("fetched_count")),
        "page_fetch_success": coerce_int(qa_summary.get("page_fetch_success_count")),
        "page_fetch_forbidden": coerce_int(qa_summary.get("page_fetch_forbidden_count")),
        "page_fetch_error": coerce_int(qa_summary.get("page_fetch_error_count")),
        "missing_topic": coerce_int(qa_summary.get("missing_topic_count")),
        "topic_coverage": qa_summary.get("topic_coverage") or {},
        "rejected_samples": qa_summary.get("rejected_samples") or [],
        "started_at": run.get("started_at"),
        "completed_at": run.get("completed_at"),
    }


def latest_run_by_source(runs: list[dict[str, Any]], source_name: str) -> dict[str, Any] | None:
    normalized = source_name.lower()
    for run in runs:
        if (run.get("source_name") or "").lower() == normalized:
            return summarize_run(run)
    return None


def build_validation_report(base_url: str, results: dict[str, FetchResult]) -> dict[str, Any]:
    health_payload = results["health"].payload if results["health"].ok else {}
    summary_payload = results["summary"].payload if results["summary"].ok else {}
    runs_payload = results["runs"].payload if results["runs"].ok and isinstance(results["runs"].payload, list) else []
    feed_payload = results["feed"].payload if results["feed"].ok and isinstance(results["feed"].payload, dict) else {}
    targets_payload = results["targets"].payload if results["targets"].ok and isinstance(results["targets"].payload, list) else []
    assessments_payload = (
        results["assessments"].payload if results["assessments"].ok and isinstance(results["assessments"].payload, list) else []
    )

    return {
        "api_base_url": base_url,
        "health": {
            "ok": results["health"].ok,
            "status_code": results["health"].status_code,
            "payload": health_payload,
            "error": results["health"].error,
        },
        "analysis": {
            "analyzed_documents": coerce_int(summary_payload.get("total_documents")),
            "positive": coerce_int(summary_payload.get("positive")),
            "neutral": coerce_int(summary_payload.get("neutral")),
            "negative": coerce_int(summary_payload.get("negative")),
            "targets_count": len(targets_payload),
            "assessments_count": len(assessments_payload),
        },
        "feed": {
            "items_count": len(feed_payload.get("items") or []),
        },
        "latest_runs": {
            "vanguard": latest_run_by_source(runs_payload, "vanguard"),
            "punch": latest_run_by_source(runs_payload, "punch"),
        },
        "recent_runs_count": len(runs_payload),
        "endpoint_status": {
            name: {
                "ok": result.ok,
                "status_code": result.status_code,
                "error": result.error,
            }
            for name, result in results.items()
        },
    }


def format_source_run(label: str, run: dict[str, Any] | None) -> list[str]:
    if run is None:
        return [f"- {label}: no recent run found"]
    return [
        f"- {label}: status={run['status']} fetched={run['fetched']} inserted={run['inserted']} "
        f"rejected={run['rejected']} duplicates={run['duplicates']}",
        f"  fetch outcomes: success={run['page_fetch_success']} forbidden={run['page_fetch_forbidden']} "
        f"errors={run['page_fetch_error']} missing_topic={run['missing_topic']}",
    ]


def format_report(report: dict[str, Any]) -> str:
    lines = [
        "Hosted ETL validation summary",
        f"API base URL: {report['api_base_url']}",
        "",
        "Health",
        f"- ok: {report['health']['ok']}",
        f"- status code: {report['health']['status_code']}",
    ]
    if report["health"]["payload"]:
        lines.append(f"- payload: {json.dumps(report['health']['payload'], sort_keys=True)}")
    if report["health"]["error"]:
        lines.append(f"- error: {report['health']['error']}")

    analysis = report["analysis"]
    lines.extend(
        [
            "",
            "Analysis",
            f"- analyzed documents: {analysis['analyzed_documents']}",
            f"- sentiment totals: positive={analysis['positive']} neutral={analysis['neutral']} negative={analysis['negative']}",
            f"- targets count: {analysis['targets_count']}",
            f"- assessments count: {analysis['assessments_count']}",
            "",
            "Feed",
            f"- items count: {report['feed']['items_count']}",
            "",
            "Latest source runs",
        ]
    )
    lines.extend(format_source_run("Vanguard", report["latest_runs"]["vanguard"]))
    lines.extend(format_source_run("Punch", report["latest_runs"]["punch"]))
    lines.extend(
        [
            "",
            "Endpoint status",
        ]
    )
    for name, status in report["endpoint_status"].items():
        lines.append(
            f"- {name}: ok={status['ok']} status_code={status['status_code']} error={status['error'] or 'none'}"
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run repeatable hosted ETL validation checks against the deployed backend.")
    parser.add_argument(
        "--api-base-url",
        default=DEFAULT_API_BASE_URL,
        help="Backend API base URL, for example https://example.azurewebsites.net/api",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Request timeout in seconds.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the validation report as JSON instead of human-readable text.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base_url = normalize_base_url(args.api_base_url)
    results = {
        "health": fetch_json(base_url, "/health", timeout=args.timeout),
        "summary": fetch_json(base_url, "/sentiment/summary", timeout=args.timeout),
        "targets": fetch_json(base_url, "/sentiment/targets", timeout=args.timeout),
        "assessments": fetch_json(base_url, "/sentiment/assessments", timeout=args.timeout),
        "feed": fetch_json(base_url, "/feed", timeout=args.timeout),
        "runs": fetch_json(base_url, "/ingest/runs", timeout=args.timeout),
    }
    report = build_validation_report(base_url, results)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
