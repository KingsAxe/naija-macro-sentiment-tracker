# Implementation Guide: Naija Macro-Sentiment Tracker

This document defines the execution standard for building the project. It is intentionally aligned to `plan.md`, the step order in `ideas-for-steps.md`, and the weekly milestones in `weekly-guide.md`.

## Build Strategy
The project should be built in four major stages:

1. Foundation: repository structure, backend scaffold, database models, migrations, and local environment setup.
2. Data pipeline: file-based ingestion first, then scraping, then Azure AI analysis.
3. Product surface: FastAPI routes, scheduler integration, and Next.js dashboard.
4. Production transition: Azure deployment, environment hardening, and cloud validation.

## Engineering Rules

- All code should be modular, typed, and documented where the logic is not obvious.
- No credentials or connection strings may be hardcoded.
- ETL logic must be reusable outside route handlers.
- Database changes must go through Alembic migrations.
- Every phase must have a local verification step before moving on.
- Azure should be used as the production target, not as the first-place integration environment.

## Phase 1: Repository and Environment Setup

### Goals
- Establish a monorepo layout that supports local development and later Azure deployment.
- Create separate backend and frontend workspaces.
- Define environment-variable handling for local and cloud use.

### Deliverables
- `/backend`
- `/frontend`
- backend virtual environment and dependency manifest
- frontend Next.js 15 app with TypeScript and Tailwind
- `.env.example` files or equivalent environment documentation
- root `.gitignore` that excludes virtual environments, build artifacts, and secrets

### Notes
- The existing local virtual environment should not define the long-term repository structure.
- Keep the application paths predictable so an agent can continue execution without reinterpreting the layout.

## Phase 2: Database and Domain Model

### Goals
- Define the core schema before building ingestion or frontend features.
- Make migrations reproducible in local development and Azure-hosted PostgreSQL.

### Required Models
- `RawText`
  - `id`
  - `source`
  - `content`
  - `published_at` or `timestamp`
  - optional ingestion metadata such as `source_url`
- `AnalyzedSentiment`
  - `id`
  - `raw_text_id`
  - `overall_sentiment`
  - `confidence_positive`
  - `confidence_neutral`
  - `confidence_negative`
- `OpinionTarget`
  - `id`
  - `analyzed_sentiment_id`
  - `target_name`
  - `target_sentiment`

### Deliverables
- SQLAlchemy models
- Pydantic response schemas
- database session and engine setup
- initial Alembic migration

## Phase 3: ETL Pipeline

### Goals
- Build one reliable ingestion path first using a local CSV or XLSX file.
- Add web scraping after the ETL pipeline shape is stable.
- Integrate Azure AI Language using opinion mining.

### Sequence
1. Implement CSV and XLSX ingestion with Pandas.
2. Treat manually collected X data as a file-based source that is added to those CSV or XLSX inputs.
3. Normalize file-based rows into the same internal structure the scraper will use.
4. Ensure the ingestion format can carry source labels such as `x_manual`, `vanguard`, and `punch`.
5. Implement basic ETL runner logic that stores raw text before analysis.
6. Add Azure AI analysis with `show_opinion_mining=True`.
7. Add batching with a maximum of 10 documents per request.
8. Add sleep and retry behavior to stay within F0 free-tier limits.
9. Add BeautifulSoup scraping for Vanguard and Punch with graceful failure handling.

### Why File-Based Ingestion Comes First
- deterministic test data
- easier debugging
- simpler repeatability for demos and capstone review
- lower dependence on changing external page structure
- compatible with manually collected X data before any live social-media integration is attempted

## Phase 4: FastAPI API and Scheduler

### Goals
- Expose stable backend endpoints after the database and ETL behavior are proven.
- Support manual ingestion control from the frontend.

### Required Endpoints
- `GET /api/sentiment/summary`
- `GET /api/sentiment/targets`
- `GET /api/feed`
- `POST /api/ingest/trigger`

### Scheduler Guidance
- APScheduler may run in the local API process during development.
- Keep scheduled ETL code thin and separate from route code.
- Design the ETL runner so it can later be invoked by a dedicated Azure job or worker without large code changes.

## Phase 5: Frontend Dashboard

### Goals
- Build the UI only after the API contract is stable.
- Prioritize useful operational views over visual polish alone.

### Core Components
- `MacroMoodChart`
- `TargetHeatmap`
- `LiveFeed`
- `ControlPanel`

### Required States
- loading
- empty
- error
- success after ingestion

## Phase 6: Local Integration Testing

### Required Checks
- backend boots successfully
- migrations apply cleanly
- CSV or XLSX ingestion populates the database
- manually collected X records can be added to a file and ingested through the same ETL path
- Azure AI analysis stores sentiment and target records
- Vanguard and Punch scraping failures do not crash the system
- frontend can fetch and display backend data
- manual ingestion from the UI updates the dashboard

## Phase 7: Azure Deployment Preparation

### Goals
- Prepare the application for cloud deployment without changing core logic.

### Deliverables
- production environment variable inventory
- deployment configuration for backend and frontend
- PostgreSQL connection configuration for Azure
- CORS updates for deployed frontend URL
- public read-only dashboard scope
- admin-only scope for uploads, ingestion, and scheduler control
- production-safe logging and startup settings

## Phase 8: Azure Deployment and Cloud Testing

### Goals
- Deploy the existing local architecture to Azure.
- Validate production behavior with real cloud services.

### Cloud Validation Checklist
- backend deployment succeeds
- frontend deployment succeeds
- backend can connect to Azure PostgreSQL
- backend can call Azure AI Language with production credentials
- API endpoints work from deployed frontend
- public users can view the dashboard without signing in
- admin-only actions are blocked for unauthenticated users and allowed for approved operators
- ingestion can be manually triggered in the cloud
- at least one complete end-to-end cloud test run is documented

## Execution Reference
Use these documents together:

- `plan.md` for scope and architecture
- `ideas-for-steps.md` for build order
- `weekly-guide.md` for milestone tracking and pacing
- `week-8-deployment-prep.md` for Week 8 hosting defaults
- `production-env-checklist.md` for hosted configuration inventory
- `azure-release-runbook.md` for first deployment execution
