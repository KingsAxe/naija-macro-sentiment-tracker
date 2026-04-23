# Project Plan: Naija Macro-Sentiment Tracker

## Objective
Build a local-first, production-oriented macroeconomic sentiment analysis platform focused on public discussion about the Nigerian economy. The project should satisfy Microsoft AI-900 Capstone expectations while also serving as a portfolio-quality system that can be developed locally and then deployed to Azure with minimal architectural change.

## Product Outcome
The finished system should:

- Ingest public text data about the Nigerian economy from local CSV or XLSX files, including manually collected X posts, and selected Nigerian news sites.
- Analyze sentiment and opinion targets using Azure AI Language with opinion mining enabled.
- Store raw and analyzed results in PostgreSQL.
- Expose sentiment summaries, target trends, recent feed items, and ingestion controls through a FastAPI API.
- Render the data in a dark-mode Next.js dashboard with charts and a live feed.
- Support a clean transition from local development to Azure hosting and cloud validation.

## Delivery Principles

### 1. Local First
All core functionality must work locally before any Azure deployment work begins. This reduces cloud cost, makes debugging faster, and avoids using Azure as the first integration environment.

### 2. File-Based Ingestion First, Scraping Second
The first stable ingestion path should be a local CSV or XLSX dataset. This should include manually collected X data when available. File-based ingestion is deterministic and easier to test. Live scraping should be added only after the database schema, ETL flow, and Azure AI integration are working end-to-end.

### 3. Keep Runtime Boundaries Clean
The ETL pipeline should remain separate from API route logic. FastAPI may trigger ETL work, but the ingestion and analysis pipeline should be implemented in reusable service and runner modules so it can later move to a dedicated Azure job if needed.

### 4. Environment Parity
Use the same application structure, environment-variable model, and database migration flow in local and Azure environments. The production transition should be mostly configuration and deployment work, not a redesign.

## Target Architecture

### Backend (`/backend`)
- Framework: FastAPI
- ORM and migrations: SQLAlchemy + Alembic
- Database: local PostgreSQL for development, Azure Database for PostgreSQL Flexible Server in production
- ETL components:
  - CSV and XLSX ingestion with Pandas
  - Manual X dataset ingestion through the same file-based ETL path
  - News scraping with BeautifulSoup for Vanguard and Punch
  - Sentiment and opinion mining with Azure AI Language
- Scheduling:
  - Local development: APScheduler is acceptable
  - Production direction: keep scheduling logic replaceable so it can move to an Azure-native scheduled job later if needed

### Frontend (`/frontend`)
- Framework: Next.js 15 with App Router
- Styling: Tailwind CSS
- Components: shadcn/ui where useful
- Theme: forced dark mode, terminal or quant-inspired visual language
- Charts: Recharts

### Data Model
- `RawText`: stores ingested text and source metadata
- `AnalyzedSentiment`: stores document-level sentiment and confidence scores
- `OpinionTarget`: stores target-level sentiment extracted from opinion mining

## Local-to-Azure Hosting Path

### Local Development
- Run FastAPI locally
- Run PostgreSQL locally
- Use local CSV or XLSX files as the first ingestion source
- Allow manually collected X data to be added to those files and processed by the same ingestion pipeline
- Validate Azure AI Language integration from the local backend
- Run the Next.js frontend locally against the local API

### Azure Deployment Target
- Frontend: Azure Static Web Apps
- Backend: Azure App Service or Azure Container Apps
- Database: Azure Database for PostgreSQL Flexible Server
- AI service: Azure AI Language

## Success Criteria
The project is ready for Azure deployment when all of the following are true:

- Local database migrations run cleanly from scratch
- CSV or XLSX ingestion works end-to-end
- Manually collected X data can be ingested through the file-based pipeline
- Azure AI sentiment and opinion mining results are stored correctly
- Scraped headlines from Vanguard and Punch can be ingested with graceful failure handling
- API endpoints return stable, frontend-ready responses
- Frontend renders charts, feed data, loading states, and empty states correctly
- Manual ingestion can be triggered from the UI
- Public users can browse the hosted dashboard without signing in
- Hosted operator actions such as ingestion and scheduler control are protected by authentication and authorization

## Planning Reference
Execution order, weekly milestones, and deployment checkpoints are defined in:

- [implementation-guide.md](C:/Users/pc/Desktop/Pro_Jets/naija-sentiment-tracker/docs/implementation-guide.md)
- [ideas-for-steps.md](C:/Users/pc/Desktop/Pro_Jets/naija-sentiment-tracker/docs/ideas-for-steps.md)
- [weekly-guide.md](C:/Users/pc/Desktop/Pro_Jets/naija-sentiment-tracker/docs/weekly-guide.md)
