from __future__ import annotations

import argparse
import logging
import sys

from app.db.session import SessionLocal
from app.services.analysis import analyze_pending_sentiments, azure_language_is_configured
from app.services.ingestion import ingest_file_to_database

logger = logging.getLogger("app.etl.runner")


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logging.getLogger("azure").setLevel(logging.WARNING)
    logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run file-based ingestion into PostgreSQL.")
    parser.add_argument(
        "--csv-path",
        default=None,
        help="Optional relative or absolute path to the source CSV/XLSX file.",
    )
    parser.add_argument(
        "--skip-analysis",
        action="store_true",
        help="Only run file ingestion and skip Azure AI sentiment analysis.",
    )
    return parser.parse_args()


def main() -> int:
    configure_logging()
    args = parse_args()

    logger.info("Starting file-based ingestion run")
    session = SessionLocal()
    try:
        result = ingest_file_to_database(session=session, file_path=args.csv_path, logger=logger)
        logger.info(
            "Ingestion completed",
            extra={
                "ingested_count": result.ingested_count,
                "skipped_count": result.skipped_count,
                "source_file": result.source_file,
            },
        )
        logger.info(
            "Ingestion summary | source_file=%s | ingested=%s | skipped=%s",
            result.source_file,
            result.ingested_count,
            result.skipped_count,
        )
        if args.skip_analysis:
            logger.info("Sentiment analysis skipped because --skip-analysis was provided")
            return 0

        if not azure_language_is_configured():
            logger.warning(
                "Azure AI Language credentials are not configured; skipping sentiment analysis"
            )
            return 0

        analysis_result = analyze_pending_sentiments(session=session, logger=logger)
        logger.info(
            "Analysis summary | analyzed=%s | targets=%s | assessments=%s | skipped=%s",
            analysis_result.analyzed_count,
            analysis_result.target_count,
            analysis_result.assessment_count,
            analysis_result.skipped_count,
        )
        return 0
    except Exception:
        logger.exception("Ingestion run failed")
        session.rollback()
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
