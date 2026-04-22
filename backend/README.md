# Backend

FastAPI application, SQLAlchemy models, and ETL services for the Naija Sentiment Tracker.

## Run

```powershell
uvicorn app.main:app --reload
```

## Planned Next Steps

- add Alembic migrations
- implement CSV ingestion service
- integrate Azure AI Language sentiment analysis
- add PostgreSQL-specific local configuration
