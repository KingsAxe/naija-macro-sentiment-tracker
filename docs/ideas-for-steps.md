# Step Order: Naija Macro-Sentiment Tracker

This file is the short execution order for building the system. It is not the full specification. Use it together with `plan.md`, `implementation-guide.md`, and `weekly-guide.md`.

## Step 1: Project Scaffolding and Database Setup
- Create the monorepo structure with `/backend` and `/frontend`.
- Set up backend dependencies and a basic FastAPI application entrypoint.
- Configure SQLAlchemy, database sessions, and Alembic.
- Implement domain models and API schemas.
- Verify the first migration runs against local PostgreSQL.

## Step 2: File-Based ETL and Azure AI Services
- Implement CSV and XLSX ingestion before live scraping.
- Allow manually collected X data to be provided through those files.
- Normalize ingested file-based data into the same internal structure that the scraper will later use.
- Implement Azure AI Language integration with `show_opinion_mining=True`.
- Add batching with a maximum of 10 documents per request.
- Add basic retry and sleep logic for F0 free-tier limits.
- Build the ETL runner that stores raw and analyzed results in PostgreSQL.

## Step 3: Add Web Scraping
- Implement BeautifulSoup scrapers for Vanguard and Punch.
- Handle parsing failures and network issues gracefully.
- Feed scraped results through the same ETL and analysis pipeline used for CSV rows.

## Step 4: FastAPI Routes and Scheduler
- Implement `/api/sentiment/summary`, `/api/sentiment/targets`, `/api/feed`, and `/api/ingest/trigger`.
- Return response data using Pydantic schemas.
- Integrate APScheduler for local development use.
- Keep scheduler logic separate enough that a future Azure job can call the same ETL runner.

## Step 5: Frontend Initialization
- Initialize the Next.js 15 app with App Router, TypeScript, and Tailwind CSS.
- Configure forced dark mode.
- Add the API client layer for `http://localhost:8000`.
- Create the first UI shells for the dashboard components.

## Step 6: Dashboard Assembly
- Populate the dashboard with live API data.
- Implement the summary chart, target view, live feed, and ingest control panel.
- Add loading, empty, and error states.

## Step 7: Local System Validation
- Run the full backend and frontend locally.
- Trigger ingestion from the UI.
- Verify database writes, API responses, and dashboard updates.

## Step 8: Azure Deployment and Cloud Testing
- Provision Azure resources only after the local system is stable.
- Deploy frontend, backend, and PostgreSQL infrastructure.
- Configure production environment variables and CORS.
- Execute end-to-end cloud validation and document the outcome.
