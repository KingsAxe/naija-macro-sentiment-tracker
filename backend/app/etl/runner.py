from __future__ import annotations

import argparse
import logging
import sys

from app.db.session import SessionLocal
from app.services.ingestion import ingest_file_to_database

logger = logging.getLogger("app.etl.runner")


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run file-based ingestion into PostgreSQL.")
    parser.add_argument(
        "--csv-path",
        default=None,
        help="Optional relative or absolute path to the source CSV/XLSX file.",
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
        return 0
    except Exception:
        logger.exception("Ingestion run failed")
        session.rollback()
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
