from pathlib import Path

import pandas as pd

from app.services.ingestion import clean_raw_dataset, prepare_clean_records


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

    assert resolved_path == Path("C:/Users/pc/Desktop/Pro_Jets/naija-sentiment-tracker/backend/data/raw_macro_data.csv")
    assert not cleaned.empty
    assert set(["source", "topic_label", "content", "published_at", "source_url"]).issubset(
        cleaned.columns
    )
    assert cleaned["topic_label"].notna().all()
