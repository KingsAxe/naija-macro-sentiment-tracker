# Naija Macro Sentiment Tracker

Local-first macroeconomic sentiment tracker for public discussion about the Nigerian economy. The current system ingests manually collected X data, stores it in PostgreSQL, analyzes sentiment and opinion targets with Azure AI Language, exposes FastAPI endpoints, and renders a live Next.js dashboard.

## Current Capabilities

- File-based ingestion for manual X datasets in CSV/XLSX form.
- Cleaning and EDA audit notebook at `backend/data/01_data_cleaning_eda.ipynb`.
- Production ETL runner with validation, deduplication, run tracking, logging, and PostgreSQL writes.
- RSS-first Vanguard and Punch news ingestion for macro-relevant business articles.
- SQLAlchemy models and Alembic migrations for:
  - raw text
  - ingestion runs
  - document sentiment
  - opinion targets
  - opinion assessments
- Azure AI Language sentiment analysis with opinion mining.
- FastAPI endpoints for summary, targets, assessments, feed, and ingestion trigger.
- Next.js dashboard wired to live backend data.

## Repository Layout

- `backend/`: FastAPI app, ETL runner, SQLAlchemy models, Alembic migrations, tests, and data files.
- `frontend/`: Next.js dashboard.
- `docs/`: planning docs, project log, and manual data contract.
- `nst/`: local Python virtual environment used for this project. It is ignored by Git.

## Environment Files

Backend:

```powershell
Copy-Item backend\.env.example backend\.env
```

Then fill `backend/.env` with local PostgreSQL and Azure AI Language values.

Frontend:

```powershell
Copy-Item frontend\.env.example frontend\.env.local
```

Default frontend API target:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

## Backend Setup

From the repository root:

```powershell
.\nst\Scripts\python.exe -m pip install -e .\backend[dev]
```

Apply database migrations:

```powershell
cd backend
..\nst\Scripts\python.exe -m alembic -c alembic.ini upgrade head
```

Run the backend API:

```powershell
cd backend
..\nst\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Useful backend URLs:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/api/health`
- `http://127.0.0.1:8000/api/sentiment/summary`
- `http://127.0.0.1:8000/api/sentiment/targets`
- `http://127.0.0.1:8000/api/sentiment/assessments`
- `http://127.0.0.1:8000/api/feed`

## ETL And Analysis

Run file ingestion plus Azure AI sentiment analysis:

```powershell
cd backend
..\nst\Scripts\python.exe -m app.etl.runner --csv-path data/raw_macro_data.csv
```

Run ingestion only, without Azure calls:

```powershell
cd backend
..\nst\Scripts\python.exe -m app.etl.runner --csv-path data/raw_macro_data.csv --skip-analysis
```

Run manual X ingestion plus Vanguard/Punch news ingestion without Azure calls:

```powershell
cd backend
..\nst\Scripts\python.exe -m app.etl.runner --csv-path data/raw_macro_data.csv --include-news --news-limit 20 --skip-analysis
```

Use `--skip-news-pages` to ingest RSS titles/summaries only without fetching article pages.

The current manual X dataset uses the contract documented at `docs/manual-x-data-contract.md`.

## Frontend Setup

From the frontend directory:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

Build check:

```powershell
cd frontend
npm run build
```

## Verification

Backend tests:

```powershell
.\nst\Scripts\python.exe -m pytest backend\tests -q --basetemp=backend\.pytest_tmp -p no:cacheprovider
```

Frontend production build:

```powershell
cd frontend
npm run build
```

Current verified local database state after Azure analysis:

- `raw_texts`: 40
- `analyzed_sentiments`: 40
- `opinion_targets`: 11
- `opinion_assessments`: 11

## Next Work

- Visually QA the dashboard against the live backend API.
- Refine dashboard layout and loading/error states.
- Analyze newly ingested Vanguard/Punch rows and review dashboard behavior with mixed X/news data.
