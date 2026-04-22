# Manual X Data Contract

This document defines the required file contract for manually collected X data before it enters the production ingestion pipeline.

## Purpose

The notebook in `backend/data/01_data_cleaning_eda.ipynb` is the audit and exploration workspace.
This contract is the fixed import rulebook used by the production ETL pipeline.

## Accepted File Types

- `.csv`
- `.xlsx`

## Required Columns

Every import file must contain these columns exactly:

- `source`
- `topic_label`
- `text_content`
- `date_published`
- `reference_url`

## Column Rules

### `source`
- Required
- Case-insensitive
- Current accepted value: `x`
- The production pipeline normalizes it to lowercase before insert

### `topic_label`
- Required
- Must not be blank after trimming whitespace
- Current accepted labels:
  - `FX Rate`
  - `Food Inflation`
  - `Fuel Price`

### `text_content`
- Required
- Must not be blank after trimming whitespace
- Production ingestion strips surrounding whitespace and repairs obvious encoding issues where possible

### `date_published`
- May be blank in rare cases
- Current accepted manual formats:
  - abbreviated month plus day, for example:
    - `Apr 18`
    - `Feb 27`
  - full numeric month/day/year, for example:
    - `4/22/2026`
- When the short month/day format is used, the pipeline interprets it using the current calendar year
- If a row is missing `date_published`, the pipeline fills it with the mode of the non-empty dates in that file

### `reference_url`
- Optional but strongly preferred
- If present, it must start with `http://` or `https://`
- Used together with source and content for deduplication

## Deduplication Rule

The production pipeline treats a row as already imported when the combination below matches an existing record:

- `source`
- `reference_url`
- `text_content`

## Normalized Output Shape

After validation and cleaning, the production ETL converts the raw file into this internal structure:

- `source`
- `topic_label`
- `content`
- `published_at`
- `source_url`

## Current Status

This contract matches the manually collected X dataset currently stored in `backend/data/raw_macro_data.csv`.
Once this file shape changes, the contract and validation helpers must be updated at the same time.
