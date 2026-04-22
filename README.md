# Naija Sentiment Tracker

Local-first macro-sentiment analysis platform focused on public discussion about the Nigerian economy.

## Workspace Layout

- `backend/`: FastAPI API, database models, ETL services, and migrations.
- `frontend/`: Next.js dashboard shell for visualizing sentiment trends.
- `docs/`: delivery plan, execution notes, and weekly milestones.

## Local Development

### Backend

1. Create a virtual environment inside `backend/.venv`.
2. Install dependencies:

```powershell
pip install -e .[dev]
```

3. Copy `.env.example` to `.env`.
4. Run the API:

```powershell
uvicorn app.main:app --reload
```

### Frontend

1. Install dependencies:

```powershell
npm install
```

2. Copy `.env.example` to `.env.local`.
3. Run the dashboard:

```powershell
npm run dev
```

## Current Status

The repository currently includes:

- backend application scaffold
- SQLAlchemy domain models and session setup
- starter API routes for health, summary, targets, feed, and manual ingest trigger
- Next.js dashboard shell with chart, feed, and control panel placeholders

The ETL pipeline, migrations, and Azure AI integration are still to be implemented.
