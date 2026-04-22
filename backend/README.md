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

## Planned Next Steps

- add Alembic migrations
- integrate Azure AI Language sentiment analysis
- add PostgreSQL-specific local configuration
