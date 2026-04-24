# Week 8 Deployment Prep

This document captures the current Azure deployment shape, the production configuration inventory, and the few remaining decisions that matter before Week 9 deployment work begins.

## Adopted Defaults

These defaults are now the working Week 8 direction unless there is an explicit change later:

1. Backend on Azure App Service
2. Frontend on Azure Static Web Apps
3. Public analysis and operations pages remain read-only
4. Scheduler remains disabled on first deploy
5. Admin protection is required before hosted uploads, ingestion, or scheduler toggles are enabled

## Current Recommended Azure Shape

### Frontend
- Service: Azure Static Web Apps
- Why:
  - best fit for a public Next.js dashboard
  - simple environment variable management
  - easy custom domain and HTTPS support

### Backend
- Recommended default: Azure App Service
- Alternative: Azure Container Apps
- Why App Service is the default:
  - simpler first deployment path
  - enough for FastAPI and the current operational scope
  - lower setup complexity for a portfolio deployment
- Why Container Apps may be chosen later:
  - better fit if the backend becomes more job-heavy or container-centric
  - easier path if scheduler logic later moves toward separate worker workloads

### Database
- Service: Azure Database for PostgreSQL Flexible Server
- Why:
  - matches the existing SQLAlchemy and Alembic flow
  - clean production target for the current local PostgreSQL model

### AI
- Service: Azure AI Language
- Why:
  - already the active production analysis engine in the codebase
  - no fallback engine is planned for deployment

## Public Vs Admin Surface

### Public
- analysis dashboard pages
- sentiment charts
- target and assessment views
- feed browsing
- operations read views, if desired

### Admin Only
- manual ingestion trigger
- future X upload/import entry points
- scheduler toggle
- any future operational upload or reprocessing action

## Production Configuration Inventory

### Backend Required
- `APP_NAME`
- `APP_ENV`
- `API_V1_PREFIX`
- `DATABASE_URL`
- `AZURE_LANGUAGE_ENDPOINT`
- `AZURE_LANGUAGE_KEY`
- `AZURE_LANGUAGE_DEFAULT_LANGUAGE`
- `AZURE_LANGUAGE_BATCH_SIZE`
- `AZURE_LANGUAGE_RETRY_ATTEMPTS`
- `AZURE_LANGUAGE_RETRY_DELAY_SECONDS`
- `AZURE_LANGUAGE_BATCH_SLEEP_SECONDS`
- `INGEST_BATCH_SIZE`
- `CSV_SOURCE_PATH`
- `FRONTEND_ORIGIN`

### Backend Optional But Important
- `AUTO_CREATE_SCHEMA_ON_STARTUP`
  - recommended production value: `false`
  - migrations should be explicit, not startup side effects
- `SCHEDULER_ENABLED`
  - recommended production value at first deploy: `false`
  - safer until admin protection is in place
- `SCHEDULER_DAILY_HOUR`
- `SCHEDULER_INCLUDE_NEWS`
- `SCHEDULER_NEWS_LIMIT`
- `SCHEDULER_SKIP_NEWS_PAGES`

### Frontend Required
- `NEXT_PUBLIC_API_BASE_URL`

## Production Defaults Recommended Right Now

- `AUTO_CREATE_SCHEMA_ON_STARTUP=false`
- `SCHEDULER_ENABLED=false`
- public dashboard enabled
- admin actions hidden or blocked until auth is implemented

## First Deployment Runtime Shape

### Backend Startup
- Run Alembic migrations explicitly during deployment or release flow
- Start the API with:
  - `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Frontend Runtime
- Build Next.js normally in the Azure Static Web Apps pipeline
- Set `NEXT_PUBLIC_API_BASE_URL` to the deployed backend URL plus `/api`

### Database Handling
- Use Azure Database for PostgreSQL Flexible Server
- Keep `AUTO_CREATE_SCHEMA_ON_STARTUP=false`
- Treat migrations as a release step, not an application boot side effect

## Important Week 8 Gaps

### 1. Hosted Auth Boundary
- public read access is allowed
- admin write actions must be protected
- recommended Azure direction: Microsoft Entra ID for admin/operator access

### 2. Scheduler Placement
- current state:
  - scheduler runs inside the API process
- acceptable for:
  - local development
  - early hosted demo if disabled or tightly controlled
- better long-term production direction:
  - move scheduled execution to a dedicated Azure job or worker

### 3. Migration Discipline
- current production-ready direction:
  - use Alembic migrations explicitly
  - do not rely on automatic schema creation at application startup

## Decisions Still Needed

These are the few remaining choices that matter.

### Decision 1: Backend Hosting
- Option A: Azure App Service
  - simpler and faster to ship
  - recommended first choice
- Option B: Azure Container Apps
  - more flexible for later worker/job separation
  - slightly more setup complexity

### Decision 2: Public Operations Page
- Option A: keep `/operations` public read-only
  - better recruiter visibility
  - exposes run metrics publicly
- Option B: keep only analysis public and protect `/operations`
  - tighter operational privacy
  - less public proof of system depth

### Decision 3: First Deployment Scheduler State
- Option A: disabled on first deploy
  - safer
  - recommended until auth is live
- Option B: enabled on first deploy
  - more automation immediately
  - higher risk if admin boundaries are not finished

## Recommended Path

For the first Azure deployment:

1. Frontend on Azure Static Web Apps
2. Backend on Azure App Service
3. Azure PostgreSQL Flexible Server
4. Azure AI Language as the only analysis engine
5. Scheduler disabled on first deploy
6. Public dashboard open for read-only browsing
7. Admin-only actions protected with Microsoft Entra ID before enabling hosted operational controls
