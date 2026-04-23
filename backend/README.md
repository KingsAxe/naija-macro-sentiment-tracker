# Backend

FastAPI application, SQLAlchemy models, and ETL services for the Naija Sentiment Tracker.

## Run

```powershell
uvicorn app.main:app --reload
```

## Run The File-Based ETL

```powershell
..\nst\Scripts\python.exe -m app.etl.runner --csv-path data/raw_macro_data.csv
```

If Azure AI Language credentials are configured, the runner will ingest pending file records and then analyze any raw texts that do not yet have sentiment results.

Use this variant to ingest data without calling Azure AI:

```powershell
..\nst\Scripts\python.exe -m app.etl.runner --csv-path data/raw_macro_data.csv --skip-analysis
```

## Planned Next Steps

- add Alembic migrations
- integrate Azure AI Language sentiment analysis
- add PostgreSQL-specific local configuration
