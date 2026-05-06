import shutil
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import pandas as pd
import pytest

from app.services.ingestion import (
    ALLOWED_TOPIC_LABELS,
    BACKEND_ROOT,
    clean_raw_dataset,
    load_raw_dataset,
    prepare_clean_records,
)

TEST_TMP_ROOT = BACKEND_ROOT / "tests_tmp"


@contextmanager
def make_workspace_temp_dir() -> Path:
    TEST_TMP_ROOT.mkdir(exist_ok=True)
    path = TEST_TMP_ROOT / uuid4().hex
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_clean_raw_dataset_fills_missing_dates_and_strips_text() -> None:
    dataframe = pd.DataFrame(
        {
            "source": [" X "],
            "topic_label": [" FX Rate "],
            "text_content": ["  Example text  "],
            "date_published": [""],
            "reference_url": [" https://example.com/post "],
        }
    )

    cleaned = clean_raw_dataset(dataframe, default_year=2026)

    assert cleaned.loc[0, "source"] == "x"
    assert cleaned.loc[0, "topic_label"] == "FX Rate"
    assert cleaned.loc[0, "content"] == "Example text"
    assert cleaned.loc[0, "source_url"] == "https://example.com/post"
    assert cleaned.loc[0, "published_at"].year == 2026


def test_prepare_clean_records_uses_manual_x_dataset() -> None:
    cleaned, resolved_path = prepare_clean_records("data/raw_macro_data.csv")

    assert resolved_path == (BACKEND_ROOT / "data/raw_macro_data.csv").resolve()
    assert not cleaned.empty
    assert set(["source", "topic_label", "content", "published_at", "source_url"]).issubset(
        cleaned.columns
    )
    assert cleaned["topic_label"].notna().all()


def test_load_raw_dataset_rejects_invalid_topic_label() -> None:
    with make_workspace_temp_dir() as tmp_dir:
        path = tmp_dir / "invalid.csv"
        pd.DataFrame(
            {
                "source": ["X"],
                "topic_label": ["Unknown Topic"],
                "text_content": ["Example text"],
                "date_published": ["Apr 18"],
                "reference_url": ["https://example.com/post"],
            }
        ).to_csv(path, index=False)

        with pytest.raises(ValueError, match="topic_label"):
            load_raw_dataset(str(path))


def test_load_raw_dataset_rejects_invalid_date_format() -> None:
    with make_workspace_temp_dir() as tmp_dir:
        path = tmp_dir / "invalid-date.csv"
        pd.DataFrame(
            {
                "source": ["X"],
                "topic_label": ["FX Rate"],
                "text_content": ["Example text"],
                "date_published": ["2026-04-18"],
                "reference_url": ["https://example.com/post"],
            }
        ).to_csv(path, index=False)

        with pytest.raises(ValueError, match="date_published"):
            load_raw_dataset(str(path))


def test_load_raw_dataset_accepts_full_numeric_date_format() -> None:
    with make_workspace_temp_dir() as tmp_dir:
        path = tmp_dir / "valid-date.csv"
        pd.DataFrame(
            {
                "source": ["X"],
                "topic_label": ["FX Rate"],
                "text_content": ["Example text"],
                "date_published": ["4/22/2026"],
                "reference_url": ["https://example.com/post"],
            }
        ).to_csv(path, index=False)

        loaded = load_raw_dataset(str(path))

        assert not loaded.empty


@pytest.mark.parametrize(
    ("topic_label", "text_content"),
    [
        ("Monetary Policy", "MPC signals tighter policy stance."),
        ("Interest Rates", "Banks raise lending rates for businesses."),
        ("Cost of Living", "Consumer prices keep squeezing households."),
        ("Power/Energy", "Electricity tariff review affects factories."),
        ("Trade/Imports", "Import duty changes affect port costs."),
        ("Banking/Credit", "Credit to private sector slows this quarter."),
        ("Budget/Fiscal Policy", "Tax revenue misses budget target."),
        ("Transport/Logistics", "Haulage costs rise on major corridors."),
        ("Employment/Labour", "Workers demand a higher minimum wage."),
        ("Business Confidence/Private Sector", "Private sector confidence eases."),
    ],
)
def test_load_raw_dataset_accepts_expanded_topic_labels(
    topic_label: str,
    text_content: str,
) -> None:
    with make_workspace_temp_dir() as tmp_dir:
        path = tmp_dir / "expanded-topics.csv"
        pd.DataFrame(
            {
                "source": ["X"],
                "topic_label": [topic_label],
                "text_content": [text_content],
                "date_published": ["Apr 18"],
                "reference_url": ["https://example.com/post"],
            }
        ).to_csv(path, index=False)

        loaded = load_raw_dataset(str(path))

        assert loaded.loc[0, "topic_label"] == topic_label


def test_allowed_topic_labels_cover_expanded_news_taxonomy() -> None:
    assert {
        "FX Rate",
        "Food Inflation",
        "Fuel Price",
        "Monetary Policy",
        "Interest Rates",
        "Cost of Living",
        "Power/Energy",
        "Trade/Imports",
        "Banking/Credit",
        "Budget/Fiscal Policy",
        "Transport/Logistics",
        "Employment/Labour",
        "Business Confidence/Private Sector",
    }.issubset(ALLOWED_TOPIC_LABELS)
