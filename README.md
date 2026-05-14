# Naija Macro Sentiment Tracker

Naija Macro Sentiment Tracker is a cloud-hosted sentiment intelligence dashboard for public discussion about the Nigerian economy. It combines manual X data ingestion, curated business-news ingestion, Azure AI sentiment analysis, operational QA tracking, and a live web dashboard for analysis and monitoring.

This project is now treated as **MVP complete** for portfolio and showcase purposes. The hosted environment remains useful and demonstrable, but ongoing ingestion and Azure AI analysis are intentionally run in a controlled, cost-aware way rather than as an always-on production workload.

## Why This Project Matters

Macroeconomic sentiment affects how people interpret inflation, exchange-rate pressure, fuel pricing, public policy, and broader business confidence. In many cases, that discussion is fragmented across social media and news coverage. This project brings those sources into one pipeline so sentiment, topical coverage, and ingestion quality can be reviewed in a more structured way.

This is not presented as a finished commercial product. It is a production-style portfolio MVP focused on Nigerian macro discourse, cloud deployment, operational observability, and disciplined iteration.

## Problem Statement

Nigerian macroeconomic discussion is noisy, fast-moving, and spread across different source types. Analysts and operators need:

- a repeatable way to ingest relevant content
- sentiment analysis that can run in the cloud
- visibility into what was accepted, rejected, duplicated, or skipped
- a frontend that shows both analytical output and ingestion health

## What The System Does

- ingests manually curated X datasets from CSV/XLSX files
- ingests curated Vanguard and Punch business news feeds
- normalizes and stores records in PostgreSQL
- analyzes sentiment and opinion targets with Azure AI Language
- tracks ingestion runs, duplicates, rejections, and QA summaries
- exposes FastAPI endpoints for dashboard consumption
- renders analysis and operations views in a Next.js frontend

## Key Features

- File-based ingestion pipeline for manual X datasets
- Hosted Vanguard and Punch news-feed ingestion
- PostgreSQL-backed sentiment and operations data model
- Azure AI Language sentiment analysis with opinion mining
- Run-level QA summaries for ingestion quality review
- Operations page with recent runs, feed inspection, and scheduler visibility
- Cloud deployment on Azure App Service and Azure Static Web Apps

## Architecture Summary

The system is a monorepo with three main layers:

- `backend/`
  FastAPI API, ETL runner, SQLAlchemy models, Alembic migrations, scheduler services, and backend tests.
- `frontend/`
  Next.js dashboard with analysis and operations views.
- `docs/`
  project planning notes, deployment references, and milestone logs.

High-level flow:

1. Manual X data or curated news items enter the ingestion pipeline.
2. Cleaned records are stored in PostgreSQL.
3. Pending records are analyzed through Azure AI Language.
4. FastAPI exposes summary, target, assessment, feed, and ingestion-run endpoints.
5. The Next.js frontend fetches live API data at runtime and renders the dashboard.

## Tech Stack

- Backend: FastAPI, SQLAlchemy, Alembic, Pandas
- Database: PostgreSQL
- Analysis: Azure AI Language
- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Deployment: Azure App Service, Azure Static Web Apps
- CI/CD: GitHub Actions

## Deployment Overview

- Backend deployment target: Azure App Service
- Frontend deployment target: Azure Static Web Apps
- Database: Azure Database for PostgreSQL Flexible Server
- Sentiment service: Azure AI Language

GitHub Actions is used for deployment, but actual secrets and deployment values must be configured in GitHub and Azure directly. They should never be committed to the repository.

## Live Demo

Current hosted frontend:

- [Live dashboard](https://thankful-beach-07fb02e0f.7.azurestaticapps.net)

If you are sharing this project externally, you may replace the link above with a different public environment later without changing the rest of the documentation.

## MVP Status And Showcase Posture

This repository should currently be read as a hosted MVP with a stable showcase posture.

What that means:

- the end-to-end system works in Azure
- the dashboard and operations page are demonstrable using the current hosted dataset
- the hosted PostgreSQL data can be treated as the active demo dataset
- ingestion and analysis are kept manual and intentional to avoid unnecessary Azure cost
- the project roadmap continues, but the core portfolio value is already proven

Recommended showcase posture:

- use the existing hosted data as the default demo dataset
- avoid unnecessary repeat ETL runs
- keep scheduled ingestion disabled
- use read-only validation checks before deciding whether a fresh hosted run is necessary

## Screenshots

Screenshots are not currently committed.

Suggested future additions:

- `docs/screenshots/analysis-page.png`
- `docs/screenshots/operations-page.png`

## Repository Layout

- `backend/`: API, ETL, models, migrations, scheduler, tests, and sample data
- `frontend/`: dashboard application
- `docs/`: deployment notes, logs, runbooks, and planning references

## Local Setup

### 1. Clone the repository

```powershell
git clone <your-repo-url>
cd naija-sentiment-tracker
```

### 2. Prepare backend environment

```powershell
Copy-Item backend\.env.example backend\.env
```

Install backend dependencies:

```powershell
.\nst\Scripts\python.exe -m pip install -e .\backend[dev]
```

Run database migrations:

```powershell
cd backend
..\nst\Scripts\python.exe -m alembic -c alembic.ini upgrade head
```

Run the backend API:

```powershell
cd backend
..\nst\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Prepare frontend environment

```powershell
Copy-Item frontend\.env.example frontend\.env.local
cd frontend
npm install
npm run dev
```

Local frontend URL:

- `http://localhost:3000`

## Environment Variables

Use the committed example files only:

- `backend/.env.example`
- `frontend/.env.example`

Use placeholder values in local or hosted configuration. Do not commit real values for:

- database connection strings
- Azure AI keys
- Azure app credentials
- GitHub Actions deployment secrets

### Backend Variables

Common backend settings:

```text
APP_NAME=Naija Sentiment Tracker API
APP_ENV=development
API_V1_PREFIX=/api
DATABASE_URL=<your_database_url>
AZURE_LANGUAGE_ENDPOINT=<your_language_endpoint>
AZURE_LANGUAGE_KEY=<your_language_key>
FRONTEND_ORIGIN=http://localhost:3000
```

### Frontend Variables

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

Hosted example:

```text
NEXT_PUBLIC_API_BASE_URL=https://your-backend-app-name.azurewebsites.net/api
```

## Running ETL And Analysis

Hosted ETL should be treated as a **manual validation action**, not a routine operation.

Run hosted ETL when:

- you have merged and deployed a backend change that affects ingestion or analysis
- you are validating a specific source-quality improvement
- you need a fresh comparison point for Vanguard or Punch behavior

Avoid hosted ETL when:

- you only need to confirm the backend is reachable
- you only need to inspect the current hosted dataset
- you are doing repeated UI or docs work
- you are not specifically testing ingestion or Azure AI analysis

The cheapest default is to preserve the current hosted dataset and validate it read-only.

Ingest and analyze manual X data:

```powershell
cd backend
..\nst\Scripts\python.exe -m app.etl.runner --csv-path data/raw_macro_data.csv
```

Ingest without Azure analysis:

```powershell
cd backend
..\nst\Scripts\python.exe -m app.etl.runner --csv-path data/raw_macro_data.csv --skip-analysis
```

Ingest manual X data plus Vanguard/Punch business feeds:

```powershell
cd backend
..\nst\Scripts\python.exe -m app.etl.runner --csv-path data/raw_macro_data.csv --include-news --news-limit 20
```

RSS-summary-only mode:

```powershell
cd backend
..\nst\Scripts\python.exe -m app.etl.runner --csv-path data/raw_macro_data.csv --include-news --news-limit 20 --skip-news-pages
```

## Hosted Validation Helper

Preferred read-only hosted validation from the repo root:

```powershell
.\scripts\validate_hosted.ps1
```

Override the hosted backend URL if needed:

```powershell
.\scripts\validate_hosted.ps1 -ApiBaseUrl https://your-backend-app.azurewebsites.net/api
```

Request JSON output:

```powershell
.\scripts\validate_hosted.ps1 -Json
```

Use the helper before running hosted ETL whenever possible. It checks backend health, recent ingestion runs, feed availability, and current analysis totals without modifying hosted data.

## Testing And Validation

### Backend tests

```powershell
.\nst\Scripts\python.exe -m pytest backend\tests -q --basetemp=backend\.pytest_tmp -p no:cacheprovider
```

### Backend lint

```powershell
.\nst\Scripts\python.exe -m ruff check backend\app backend\tests
```

### Frontend build

```powershell
cd frontend
npm run build
```

### Frontend lint

`next lint` is not currently configured to run non-interactively in this repository. That is a known repo setup item, not a hidden passing check.

## Current System Status

MVP-complete capabilities:

Confirmed working:

- Azure backend deployment
- GitHub Actions OIDC and RBAC deployment path
- Azure PostgreSQL connection
- Alembic migrations
- X/manual CSV ingestion
- Vanguard/Punch hosted news ingestion
- Azure AI Language sentiment analysis
- frontend runtime data fetching
- backend CORS configuration for the hosted frontend
- operations page ingestion metrics and QA summaries

Current operating posture:

- hosted dashboard is active and presentable
- hosted data is preserved as demo/showcase data
- validation is preferred over repeated ingestion
- scheduled ingestion should remain disabled unless there is a deliberate reason to change posture

## Known Limitations

- Vanguard article page fetches can return `403 Forbidden` in Azure, which limits page-text enrichment reliability for some news items.
- Vanguard often falls back to RSS summary input because of page-fetch blocking, so opinion-mining quality can be lower than for Punch.
- Punch article fetching works better, but repeated validation runs still become duplicate-heavy over time.
- News taxonomy quality is improving, but still evolving.
- Rejected-news QA visibility exists, but classification coverage can still be refined further.
- Opinion-mining yield for hosted news analysis remains lower than desired.
- Azure AI Language usage is cost-sensitive; repeated hosted ETL runs should be intentional and limited.
- Full automation of the hosted ingestion pipeline is intentionally paused until cost, source reliability, and operating posture are better defined.
- Frontend lint is not yet configured for non-interactive CI-style execution in the current repo setup.

## Roadmap

Current improvement focus:

1. Document and preserve the current MVP showcase posture
2. Tune manual operating guidance and cost-aware validation habits
3. Reassess whether scheduler defaults or further automation are worth the cost
4. Resume feature development only where the portfolio value clearly outweighs the maintenance burden

## Additional Documentation

- `backend/README.md` for backend-specific commands
- `docs/project-log.md` for milestone history
- `docs/week-9-deployment-notes.md` for Azure deployment lessons learned
- `docs/production-env-checklist.md` for hosted configuration guidance
- `docs/azure-release-runbook.md` for deployment sequence reference

## License

This repository is currently published with the included `LICENSE` file.
