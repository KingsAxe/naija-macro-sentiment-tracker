# Naija Macro Sentiment Tracker

Cloud-hosted macroeconomic sentiment intelligence platform for public discussion about the Nigerian economy. The current system ingests manually collected X data plus curated news sources, stores it in PostgreSQL, analyzes sentiment and opinion targets with Azure AI Language, exposes FastAPI endpoints, and renders a live Next.js dashboard.

## Current Capabilities

- File-based ingestion for manual X datasets in CSV/XLSX form.
- Cleaning and EDA audit notebook at `backend/data/01_data_cleaning_eda.ipynb`.
- Production ETL runner with validation, deduplication, run tracking, QA summaries, and PostgreSQL writes.
- RSS-first Vanguard and Punch news ingestion for macro-relevant business articles.
- Daily scheduler support with API toggle control, disabled by default.
- SQLAlchemy models and Alembic migrations for:
  - raw text
  - ingestion runs
  - document sentiment
  - opinion targets
  - opinion assessments
- Azure AI Language sentiment analysis with opinion mining.
- FastAPI endpoints for summary, targets, assessments, feed, ingestion runs, and scheduler control.
- Next.js dashboard split into analysis and operations views, wired to live backend data.

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
Scheduler settings are optional and default to disabled.
Set `FRONTEND_ORIGIN` if your Next.js app is served from a different host.

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
- `http://127.0.0.1:8000/api/ingest/runs`
- `http://127.0.0.1:8000/api/ingest/scheduler`

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

Daily scheduler config lives in `backend/.env`:

```text
SCHEDULER_ENABLED=false
SCHEDULER_DAILY_HOUR=6
SCHEDULER_INCLUDE_NEWS=true
SCHEDULER_NEWS_LIMIT=20
SCHEDULER_SKIP_NEWS_PAGES=true
```

Runtime scheduler toggle:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/ingest/scheduler -ContentType "application/json" -Body '{"enabled":true}'
```

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

Pages:

```text
http://localhost:3000/
http://localhost:3000/operations
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

- Review ingestion-run QA summaries against live news refreshes.
- Analyze newly ingested Vanguard/Punch rows and review dashboard behavior with mixed X/news data.
- Add deeper UI drill-down only if it helps explain the analysis better.
- Use [docs/week-8-deployment-prep.md](C:/Users/pc/Desktop/Pro_Jets/naija-sentiment-tracker/docs/week-8-deployment-prep.md) as the Week 8 deployment prep reference.
