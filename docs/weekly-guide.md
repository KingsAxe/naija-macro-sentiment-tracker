# Weekly Build Guide: Naija Macro-Sentiment Tracker

This guide converts the project plan into weekly milestones from initial setup through Azure deployment and cloud testing. Each week has a goal, concrete tasks, and an exit criterion so progress is easy to track.

## Week 0: Planning Alignment

### Goal
Align scope, build order, and delivery checkpoints before writing production code.

### Tasks
- Finalize `plan.md`, `implementation-guide.md`, and `ideas-for-steps.md`.
- Confirm the system will be built local-first.
- Confirm file-based ingestion as the first stable data source.
- Confirm the Azure target architecture and hosting choices.

### Exit Criteria
- All docs agree on architecture, order of work, and deployment target.
- Weekly milestones are accepted as the working delivery plan.

## Week 1: Monorepo and Environment Setup

### Goal
Create the repository structure and local development foundations.

### Tasks
- Create `/backend` and `/frontend`.
- Set up the backend Python environment and dependency manifest.
- Initialize the Next.js frontend with TypeScript and Tailwind.
- Add environment-variable templates and secret-handling rules.
- Add `.gitignore` rules for local environments, build output, and secrets.

### Exit Criteria
- Backend and frontend start independently in local development.
- The repository structure is stable enough for continued implementation.

## Week 2: Database Schema and Migrations

### Goal
Stabilize the data model before any complex integration work.

### Tasks
- Configure SQLAlchemy and Alembic.
- Implement `RawText`, `AnalyzedSentiment`, and `OpinionTarget`.
- Add Pydantic schemas for API responses.
- Run the initial migration against local PostgreSQL.
- Verify records can be created and queried locally.

### Exit Criteria
- Local Postgres is connected.
- Migrations run cleanly from a fresh database state.
- Core relationships are working as expected.

## Week 3: File-Based ETL Pipeline

### Goal
Build one deterministic end-to-end ingestion path.

### Tasks
- Add a sample CSV dataset for local development and testing.
- Add support for XLSX input using the same ingestion flow.
- Define the file schema for manually collected X data.
- Implement CSV and XLSX ingestion with Pandas.
- Normalize records into an internal ingestion format.
- Build an ETL runner that stores raw text and analysis outputs.
- Add basic logging around ingestion counts and failures.

### Exit Criteria
- A CSV or XLSX file can be ingested locally end-to-end.
- Manually collected X data can be added to that file-based pipeline without schema changes.
- Raw text records are written to PostgreSQL through the ETL flow.

## Week 4: Azure AI Language Integration

### Goal
Add sentiment and opinion mining to the working ETL pipeline.

### Tasks
- Implement Azure AI Language client configuration.
- Enable `show_opinion_mining=True`.
- Add batch processing with a maximum of 10 documents per request.
- Add retry and sleep logic to respect F0 free-tier limits.
- Persist document sentiment and target-level sentiment to the database.

### Exit Criteria
- CSV-ingested records are analyzed successfully through Azure AI Language.
- Sentiment and opinion targets are stored correctly in PostgreSQL.

## Week 5: Scraping and Backend API

### Goal
Extend ingestion sources and expose read APIs for the frontend.

### Tasks
- Implement BeautifulSoup scrapers for Vanguard and Punch.
- Ensure scraped Vanguard and Punch items are normalized into the same pipeline used for manual X file imports.
- Add graceful handling for parser failures, timeouts, and unexpected HTML changes.
- Expose backend endpoints for summary, targets, feed, and manual trigger.
- Validate response schemas and basic query performance.

### Exit Criteria
- The backend can ingest manual file-based data, including X data, plus scraped Vanguard and Punch headlines.
- API endpoints return consistent data for frontend consumption.

## Week 6: Scheduler and Frontend Shell

### Goal
Connect product controls and presentation layers.

### Tasks
- Integrate APScheduler for local development.
- Ensure the manual trigger path calls the ETL runner safely.
- Build the first version of the Next.js dashboard shell.
- Add API client utilities and component placeholders.
- Configure forced dark mode and the intended visual style.

### Exit Criteria
- Manual ingestion can be triggered through the backend.
- The frontend loads and can call backend endpoints.

## Week 7: Dashboard Completion and Local QA

### Goal
Complete the user-facing dashboard and verify the full local system.

### Tasks
- Implement `MacroMoodChart`, `TargetHeatmap`, `LiveFeed`, and `ControlPanel`.
- Add loading, empty, and error states.
- Trigger ingestion from the UI and verify the dashboard updates.
- Fix integration issues between frontend, backend, database, and Azure AI.
- Document the local run workflow.

### Exit Criteria
- The complete local system runs end-to-end.
- A user can trigger ingestion and see updated sentiment data in the dashboard.

## Week 8: Azure Preparation

### Goal
Prepare the local system for a clean Azure transition.

### Tasks
- Define production environment variables and deployment settings.
- Choose final Azure hosting targets for backend and frontend.
- Prepare PostgreSQL connection settings for Azure Flexible Server.
- Define the public read-only dashboard surface for hosted users.
- Define admin authentication and authorization boundaries for hosted operations.
- Decide which routes and UI controls remain public read-only and which require signed-in operator access.
- Review CORS, startup commands, and logging settings for production.
- Identify which local scheduler behavior should remain in the API and which should later become a dedicated Azure job.

### Exit Criteria
- The project has a documented, environment-specific deployment configuration.
- No core logic depends on local-only assumptions.

## Week 9: Azure Deployment and Cloud Testing

### Goal
Deploy the system and validate production behavior in Azure.

### Tasks
- Provision Azure PostgreSQL, Azure AI Language access, backend hosting, and frontend hosting.
- Deploy the backend and connect it to Azure PostgreSQL.
- Deploy the frontend and configure it against the deployed API.
- Implement and validate hosted admin protection for ingestion, uploads, and scheduler controls.
- Confirm public users can still open and browse the dashboard without signing in.
- Run at least one complete cloud ingestion and dashboard validation cycle.
- Document deployment issues, fixes, and final working URLs.

### Exit Criteria
- The application is running in Azure.
- End-to-end ingestion, storage, API access, and frontend rendering work in the cloud.

## Tracking Rules

- Do not start the next week until the current week exit criteria are met or explicitly waived.
- If a week slips, record the blocker and re-plan the remaining milestones instead of silently compressing the schedule.
- When an agent is implementing, it should treat the current week tasks as the allowed scope unless asked to pull work forward.
