# Backend

FastAPI, SQLAlchemy, Alembic, ETL, and Azure AI Language integration for the Naija Macro Sentiment Tracker.

## Run API

```powershell
..\nst\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Run Migrations

```powershell
..\nst\Scripts\python.exe -m alembic -c alembic.ini upgrade head
```

## Run ETL

Ingest and analyze:

```powershell
..\nst\Scripts\python.exe -m app.etl.runner --csv-path data/raw_macro_data.csv
```

Ingest only:

```powershell
..\nst\Scripts\python.exe -m app.etl.runner --csv-path data/raw_macro_data.csv --skip-analysis
```

Ingest manual X data plus Vanguard/Punch business feed articles:

```powershell
..\nst\Scripts\python.exe -m app.etl.runner --csv-path data/raw_macro_data.csv --include-news --news-limit 20
```

Use `--skip-news-pages` when you only want RSS titles/summaries and do not want to fetch article pages.

## Scheduler

Daily scheduler config is read from `backend/.env` and is disabled by default:

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

Enable it at runtime:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/ingest/scheduler -ContentType "application/json" -Body '{"enabled":true}'
```

Recent ingestion runs and QA summaries:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/ingest/runs
```

## Test

From the repository root:

```powershell
.\nst\Scripts\python.exe -m pytest backend\tests -q --basetemp=backend\.pytest_tmp -p no:cacheprovider
```
