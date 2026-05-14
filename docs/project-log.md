# Project Log

This file records the implementation status by weekly milestone so the project can be reviewed without reconstructing progress from commits or chat history.

## Week 1 Summary: Monorepo and Environment Setup

### Scope Completed
- Created the stable repository layout with `backend/`, `frontend/`, and `docs/`.
- Added backend packaging and dependency management through `backend/pyproject.toml`.
- Added frontend project scaffolding through `frontend/package.json`, TypeScript config, Tailwind config, and App Router structure.
- Added environment templates for backend and frontend.
- Added root ignore rules for local environments, generated artifacts, and secret files.

### Verification Completed
- Installed backend dependencies into the local `nst` environment.
- Installed frontend dependencies with `npm install`.
- Built the frontend successfully with `npm run build`.
- Verified backend routes respond through local smoke tests using FastAPI `TestClient`.

### Outcome
Week 1 is complete. The repository has a runnable backend and frontend foundation for continued implementation.

## Week 2 Summary: Database Schema and Migrations

### Scope Completed
- Implemented the core SQLAlchemy models:
  - `RawText`
  - `AnalyzedSentiment`
  - `OpinionTarget`
- Added database base class, engine/session wiring, and API schemas.
- Added shared database URL resolution logic for backend runtime and Alembic.
- Configured Alembic to resolve `backend/.env` reliably.
- Generated the initial Alembic migration in `backend/alembic/versions/`.
- Applied the migration to local PostgreSQL.

### Verification Completed
- Confirmed PostgreSQL was running locally on `localhost:5432`.
- Confirmed the target database exists and is reachable.
- Applied `alembic upgrade head` successfully.
- Verified the expected database tables were created.
- Performed a create/query smoke test against PostgreSQL.
- Ran backend smoke tests successfully with `pytest`.

### Outcome
Week 2 is complete. PostgreSQL is configured as the active backend database target.

## Week 3 Summary: File-Based ETL Pipeline

### Scope Completed
- Finalized the manual X CSV/XLSX ingestion contract.
- Added notebook-based cleaning and EDA support for the manually collected X dataset.
- Implemented production cleaning and normalization with Pandas.
- Added the ETL runner for file-based ingestion into PostgreSQL.
- Preserved `topic_label` through ingestion and feed exposure.

### Outcome
Week 3 is complete. Manual X data can be validated, cleaned, and written into PostgreSQL through the production ingestion path.

## Week 4 Summary: Azure AI Language Integration

### Scope Completed
- Added Azure AI Language configuration and retry controls.
- Implemented batch sentiment analysis with opinion mining.
- Persisted:
  - `AnalyzedSentiment`
  - `OpinionTarget`
  - `OpinionAssessment`
- Updated the ETL runner so ingestion and Azure analysis can run in one command.
- Added automated tests for analysis persistence and API responses.

### Outcome
Week 4 is complete. The backend can analyze pending raw documents through Azure AI Language and persist the results.

## Week 5 Summary: Source Expansion and Ingestion Safeguards

### Scope Completed
- Added RSS-first Vanguard and Punch ingestion into the same normalized pipeline used for manual X data.
- Added ingestion-run tracking with duplicate and rejection visibility.
- Added source-aware QA summaries for news ingestion runs.
- Added API support for recent ingestion runs and scheduler status.
- Verified live news ingestion against Vanguard and Punch feeds.

### Outcome
Week 5 is complete. The application supports manual X data plus curated news ingestion with observable run quality.

## Week 6 Summary: Scheduler and Frontend Shell

### Scope Completed
- Added an env-driven daily scheduler that is disabled by default and can be toggled at runtime.
- Added scheduler status and toggle endpoints.
- Added CORS support for browser-based scheduler control.
- Refined the frontend into a restrained black/neutral visual system.
- Added dashboard visibility for scheduler state and ingestion QA.

### Outcome
Week 6 is complete. The system now has operational controls, tracked ingestion quality, and a production-style dashboard shell.

## Week 7 Summary: Dashboard Completion and Local QA

### Scope Completed
- Split the frontend into dedicated analysis and operations pages.
- Added a shared top bar with scheduler visibility and operational navigation.
- Added sentiment plotting, source-performance comparison, and clearer analysis reading guidance.
- Added dashboard-side manual ingestion triggering on the operations page.
- Verified the frontend can call backend endpoints and refresh after operational actions.

### Outcome
Week 7 is complete. The dashboard is now a working analysis and operations surface with UI-triggered ingestion and local verification paths.

## Week 8 Summary: Deployment Preparation

### Scope Completed
- Documented production environment requirements for backend and frontend deployment.
- Added GitHub Actions deployment guidance for Azure hosting.
- Prepared deployment checklists and release runbooks for Week 9 execution.

### Outcome
Week 8 is complete. Deployment prerequisites and operator guidance were documented before the hosted rollout.

## Week 9 Summary: Azure Deployment and Cloud Validation

### Scope Completed
- Connected Azure Static Web Apps to the repository and corrected the generated frontend workflow for the monorepo structure.
- Added build-time frontend API base URL injection for hosted deployment.
- Configured Azure App Service startup behavior for the FastAPI backend.
- Diagnosed and resolved the missing dependency install issue in Azure App Service.
- Fixed a CI-only backend test failure caused by a hardcoded local Windows path.
- Resolved GitHub Actions Azure login failures by fixing RBAC assignment for the deployment identity.
- Applied Alembic migrations against Azure PostgreSQL.
- Verified hosted ingestion for manual X data and curated Vanguard/Punch feeds.
- Verified Azure AI Language analysis in the hosted environment.
- Switched the frontend to runtime API fetching so the dashboard works correctly on Azure Static Web Apps Free.
- Fixed hosted frontend API base URL wiring and backend CORS configuration.
- Verified that the live frontend displays hosted backend data and operations metrics.

### Outcome
Week 9 is complete. The hosted backend, hosted frontend, Azure database, Azure AI analysis, and operations monitoring flow have all been validated in Azure.

## Week 10 Summary: News Classification Quality

### Scope Completed
- Expanded the macro topic taxonomy beyond the original three labels.
- Added rejected headline QA sampling to ingestion run summaries.
- Surfaced rejected headline samples in the operations view for review.

### Outcome
Week 10 is complete. The project now has broader news-topic coverage and better visibility into classification misses.

## Week 11 Summary: Page-Text Reclassification And Hosted Validation Hardening

### Scope Completed
- Added a second-pass topic classification path that retries unmatched news items using fetched article page text.
- Preserved safe fallback behavior when page fetches fail.
- Added fetch-outcome tracking so hosted validation can distinguish successful article fetches from blocked or failed page requests.

### Current Observation
- Punch article-page fetching works in Azure and can provide richer text for downstream analysis.
- Vanguard article-page fetching can return `403 Forbidden` in Azure, so Vanguard often falls back to RSS summary input and may produce lower opinion-mining yield than Punch.
- Hosted validation is now easier to repeat through read-only helper commands from the repo root.

### Outcome
Week 11 is complete. The project now has stronger hosted validation, clearer source-specific fetch behavior, and better visibility into ingestion quality and opinion-mining yield.

## Week 12 Summary: MVP Showcase Posture

### Scope Completed
- Reassessed the project as a portfolio MVP rather than an always-on production workload.
- Defined a cost-aware hosted operating posture.
- Preserved the current hosted dataset as the default demo/showcase dataset.
- Shifted validation guidance toward read-only helper-based checks before any new hosted ETL run.

### Outcome
Week 12 is complete. The project is now treated as MVP complete, with future work intentionally slowed until the value of additional Azure usage clearly outweighs the cost.

## Current Project State

The project is currently MVP complete and positioned for sustainable portfolio review.

Confirmed working:
- Azure backend deployment
- Azure PostgreSQL connection
- Alembic migrations
- manual X ingestion
- Vanguard/Punch hosted news ingestion
- Azure AI Language sentiment analysis
- frontend runtime data fetching
- operations page ingestion metrics and QA summaries

Current operating posture:
- preserve the existing hosted dataset as demo data
- prefer read-only validation over repeated hosted ETL runs
- keep scheduler-driven ingestion disabled
- continue development only where the engineering or portfolio value is clearly justified

## Current Milestone Assessment

- Week 1: complete
- Week 2: complete
- Week 3: complete
- Week 4: complete
- Week 5: complete
- Week 6: complete
- Week 7: complete
- Week 8: complete
- Week 9: complete
- Week 10: complete
- Week 11: complete
- Week 12: complete

## Next Planned Phase

Recommended next backlog order:

1. maintain and document the MVP showcase posture
2. only run hosted ETL for targeted backend validation
3. reassess scheduler defaults before considering automation
4. resume larger feature work only if the cost and maintenance tradeoff remains acceptable
