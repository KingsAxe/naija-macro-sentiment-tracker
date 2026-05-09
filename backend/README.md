# Backend

This backend provides the API, ETL services, database models, migrations, scheduler support, and Azure AI Language integration for Naija Macro Sentiment Tracker.

## Responsibilities

- ingest manual X datasets from CSV/XLSX files
- ingest curated Vanguard and Punch business-news feeds
- normalize and persist records in PostgreSQL
- analyze pending records with Azure AI Language
- expose API routes for summaries, targets, assessments, feed data, scheduler status, and ingestion-run QA

## Run The API

From the repository root:

```powershell
cd backend
..\nst\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Run Migrations

```powershell
cd backend
..\nst\Scripts\python.exe -m alembic -c alembic.ini upgrade head
```

## Run ETL

Ingest and analyze manual X data:

```powershell
cd backend
..\nst\Scripts\python.exe -m app.etl.runner --csv-path data/raw_macro_data.csv
```

Ingest only:

```powershell
cd backend
..\nst\Scripts\python.exe -m app.etl.runner --csv-path data/raw_macro_data.csv --skip-analysis
```

Ingest manual X data plus Vanguard/Punch business feeds:

```powershell
cd backend
..\nst\Scripts\python.exe -m app.etl.runner --csv-path data/raw_macro_data.csv --include-news --news-limit 20
```

Use RSS summary-only mode when you want to skip article page fetches:

```powershell
cd backend
..\nst\Scripts\python.exe -m app.etl.runner --csv-path data/raw_macro_data.csv --include-news --news-limit 20 --skip-news-pages
```

## Scheduler

Scheduler settings are read from `backend/.env` and are disabled by default.

Example placeholders:

```text
FRONTEND_ORIGIN=http://localhost:3000
SCHEDULER_ENABLED=false
SCHEDULER_DAILY_HOUR=6
SCHEDULER_INCLUDE_NEWS=true
SCHEDULER_NEWS_LIMIT=20
SCHEDULER_SKIP_NEWS_PAGES=true
```

Check scheduler status:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/ingest/scheduler
```

Enable the scheduler at runtime:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/ingest/scheduler -ContentType "application/json" -Body '{"enabled":true}'
```

Inspect recent ingestion runs:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/ingest/runs
```

## Validation

Backend tests:

```powershell
.\nst\Scripts\python.exe -m pytest backend\tests -q --basetemp=backend\.pytest_tmp -p no:cacheprovider
```

Backend lint:

```powershell
.\nst\Scripts\python.exe -m ruff check backend\app backend\tests
```

## Notes

- Use `backend/.env.example` as the configuration template.
- Keep real database URLs, Azure keys, and deployment credentials out of the repository.
- For the broader project overview, deployment summary, and roadmap, see the root `README.md`.
