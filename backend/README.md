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

## Test

From the repository root:

```powershell
.\nst\Scripts\python.exe -m pytest backend\tests -q --basetemp=backend\.pytest_tmp -p no:cacheprovider
```
