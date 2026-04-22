from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import RawText
from app.schemas.sentiment import IngestTriggerResponse

settings = get_settings()
BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_FILE = "data/raw_macro_data.csv"
SUPPORTED_FILE_SUFFIXES = {".csv", ".xlsx"}
REQUIRED_COLUMNS = {
    "source",
    "topic_label",
    "text_content",
    "date_published",
    "reference_url",
}
REQUIRED_NON_EMPTY_COLUMNS = {"source", "topic_label", "text_content"}
ALLOWED_SOURCE_VALUES = {"x"}
ALLOWED_TOPIC_LABELS = {"FX Rate", "Food Inflation", "Fuel Price"}
LAGOS_TZ = ZoneInfo("Africa/Lagos")
MANUAL_DATE_FORMATS = ("%b %d", "%m/%d/%Y")


@dataclass(slots=True)
class IngestionRunResult:
    source_file: str
    ingested_count: int
    skipped_count: int


def _repair_text(value: str) -> str:
    suspicious_tokens = ("â€", "â€™", "â€œ", "â€", "â€”")
    if any(token in value for token in suspicious_tokens):
        try:
            return value.encode("latin1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return value
    return value


def resolve_ingestion_file(file_path: str | None = None) -> Path:
    if file_path:
        configured_path = file_path
    else:
        preferred_path = (BACKEND_ROOT / DEFAULT_SOURCE_FILE).resolve()
        configured_path = str(preferred_path) if preferred_path.exists() else settings.csv_source_path
    path = Path(configured_path)
    if not path.is_absolute():
        path = (BACKEND_ROOT / path).resolve()
    return path


def _validate_required_columns(dataframe: pd.DataFrame) -> None:
    missing_columns = REQUIRED_COLUMNS.difference(dataframe.columns)
    if missing_columns:
        raise ValueError(f"Source file is missing required columns: {sorted(missing_columns)}")


def _validate_file_contract(dataframe: pd.DataFrame) -> None:
    working = dataframe.copy()
    for column in REQUIRED_COLUMNS:
        working[column] = working[column].fillna("").astype(str).map(str.strip)

    for column in REQUIRED_NON_EMPTY_COLUMNS:
        blank_count = (working[column] == "").sum()
        if blank_count:
            raise ValueError(f"Column '{column}' contains {blank_count} blank value(s).")

    normalized_sources = {value.lower() for value in working["source"].unique() if value}
    invalid_sources = sorted(normalized_sources.difference(ALLOWED_SOURCE_VALUES))
    if invalid_sources:
        raise ValueError(
            f"Column 'source' contains unsupported value(s): {invalid_sources}. "
            f"Allowed values: {sorted(ALLOWED_SOURCE_VALUES)}"
        )

    topic_labels = {value for value in working["topic_label"].unique() if value}
    invalid_topics = sorted(topic_labels.difference(ALLOWED_TOPIC_LABELS))
    if invalid_topics:
        raise ValueError(
            f"Column 'topic_label' contains unsupported value(s): {invalid_topics}. "
            f"Allowed values: {sorted(ALLOWED_TOPIC_LABELS)}"
        )

    non_empty_dates = working.loc[working["date_published"] != "", "date_published"]
    parsed_dates = non_empty_dates.map(_parse_manual_date)
    if parsed_dates.isna().any():
        invalid_dates = non_empty_dates.loc[parsed_dates.isna()].tolist()
        raise ValueError(
            f"Column 'date_published' contains unsupported value(s): {invalid_dates}. "
            "Expected format like 'Apr 18' or '4/22/2026'."
        )

    invalid_urls = [
        value
        for value in working["reference_url"].tolist()
        if value and not (value.startswith("http://") or value.startswith("https://"))
    ]
    if invalid_urls:
        raise ValueError(
            f"Column 'reference_url' contains invalid URL value(s): {invalid_urls[:5]}"
        )


def load_raw_dataset(file_path: str | None = None) -> pd.DataFrame:
    resolved_path = resolve_ingestion_file(file_path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"CSV source not found at {resolved_path}.")

    if resolved_path.suffix.lower() not in SUPPORTED_FILE_SUFFIXES:
        raise ValueError(
            f"Unsupported file type '{resolved_path.suffix}'. "
            f"Supported types: {sorted(SUPPORTED_FILE_SUFFIXES)}"
        )

    if resolved_path.suffix.lower() == ".xlsx":
        dataframe = pd.read_excel(resolved_path)
    else:
        dataframe = pd.read_csv(resolved_path)

    _validate_required_columns(dataframe)
    _validate_file_contract(dataframe)
    return dataframe


def _parse_manual_date(value: str, default_year: int | None = None) -> pd.Timestamp | pd.NaT:
    normalized = value.strip()
    if not normalized:
        return pd.NaT

    year = default_year or datetime.now(tz=LAGOS_TZ).year

    try:
        parsed = datetime.strptime(f"{normalized} {year}", "%b %d %Y")
        return pd.Timestamp(parsed)
    except ValueError:
        pass

    try:
        parsed = datetime.strptime(normalized, "%m/%d/%Y")
        return pd.Timestamp(parsed)
    except ValueError:
        return pd.NaT


def clean_raw_dataset(dataframe: pd.DataFrame, default_year: int | None = None) -> pd.DataFrame:
    working = dataframe.copy()
    current_year = default_year or datetime.now(tz=LAGOS_TZ).year

    for column in ["source", "topic_label", "text_content", "date_published", "reference_url"]:
        working[column] = working[column].fillna("").astype(str).map(str.strip)

    working["source"] = working["source"].map(str.lower)
    working["text_content"] = working["text_content"].map(_repair_text)
    working["reference_url"] = working["reference_url"].replace("", pd.NA)

    parsed_dates = working["date_published"].replace("", pd.NA).map(
        lambda value: _parse_manual_date(value, default_year=current_year)
        if pd.notna(value)
        else pd.NaT
    )

    default_timestamp = (
        parsed_dates.dropna().mode().iloc[0]
        if not parsed_dates.dropna().empty
        else pd.Timestamp(datetime(current_year, 1, 1))
    )
    parsed_dates = parsed_dates.fillna(default_timestamp)
    parsed_dates = parsed_dates.map(lambda value: value.to_pydatetime().replace(tzinfo=LAGOS_TZ))

    cleaned = pd.DataFrame(
        {
            "source": working["source"],
            "topic_label": working["topic_label"],
            "content": working["text_content"],
            "published_at": parsed_dates,
            "source_url": working["reference_url"],
        }
    )

    cleaned["content"] = cleaned["content"].map(str.strip)
    cleaned = cleaned.loc[cleaned["content"] != ""].drop_duplicates(
        subset=["source", "source_url", "content"],
        keep="first",
    )
    return cleaned.reset_index(drop=True)


def prepare_clean_records(file_path: str | None = None) -> tuple[pd.DataFrame, Path]:
    resolved_path = resolve_ingestion_file(file_path)
    raw = load_raw_dataset(str(resolved_path))
    cleaned = clean_raw_dataset(raw)
    return cleaned, resolved_path


def bulk_insert_clean_records(
    session: Session,
    cleaned: pd.DataFrame,
) -> tuple[int, int]:
    if cleaned.empty:
        return 0, 0

    source_urls = [value for value in cleaned["source_url"].dropna().tolist() if value]
    contents = cleaned["content"].tolist()

    query = select(RawText.id, RawText.source, RawText.topic_label, RawText.source_url, RawText.content)
    conditions = []
    if source_urls:
        conditions.append(RawText.source_url.in_(source_urls))
    if contents:
        conditions.append(RawText.content.in_(contents))
    if conditions:
        query = query.where(or_(*conditions))

    existing_rows = session.execute(query).all() if conditions else []
    existing_rows_by_key = {
        (
            row.source,
            row.source_url or None,
            row.content,
        ): row
        for row in existing_rows
    }

    payloads: list[dict[str, object]] = []
    skipped_count = 0
    for row in cleaned.to_dict(orient="records"):
        key = (row["source"], row["source_url"] or None, row["content"])
        existing_row = existing_rows_by_key.get(key)
        if existing_row is not None:
            if not existing_row.topic_label and row["topic_label"]:
                session.query(RawText).filter(RawText.id == existing_row.id).update(
                    {"topic_label": row["topic_label"]},
                    synchronize_session=False,
                )
            skipped_count += 1
            continue

        payloads.append(
            {
                "source": row["source"],
                "topic_label": row["topic_label"],
                "content": row["content"],
                "source_url": row["source_url"] or None,
                "published_at": row["published_at"],
            }
        )
        existing_rows_by_key[key] = row
    if payloads:
        session.bulk_insert_mappings(RawText, payloads)
    session.commit()

    return len(payloads), skipped_count


def ingest_file_to_database(
    session: Session,
    file_path: str | None = None,
    logger: logging.Logger | None = None,
) -> IngestionRunResult:
    cleaned, resolved_path = prepare_clean_records(file_path=file_path)
    if logger:
        logger.info("Prepared %s cleaned records from %s", len(cleaned), resolved_path)

    ingested_count, skipped_count = bulk_insert_clean_records(session=session, cleaned=cleaned)
    if logger:
        logger.info(
            "Database write complete for %s | inserted=%s | skipped=%s",
            resolved_path,
            ingested_count,
            skipped_count,
        )

    return IngestionRunResult(
        source_file=str(resolved_path),
        ingested_count=ingested_count,
        skipped_count=skipped_count,
    )


def trigger_ingestion(session: Session) -> IngestTriggerResponse:
    result = ingest_file_to_database(session=session)

    return IngestTriggerResponse(
        status="completed",
        detail="File-based ingestion finished. Sentiment analysis is not wired yet.",
        ingested_count=result.ingested_count,
        skipped_count=result.skipped_count,
    )
