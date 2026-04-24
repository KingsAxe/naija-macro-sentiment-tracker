# GitHub Actions Setup

This document covers the current recommended CI/CD shape for Azure deployment.

## Backend Deployment

The backend is configured to deploy to Azure App Service through:

- [backend-appservice.yml](C:/Users/pc/Desktop/Pro_Jets/naija-sentiment-tracker/.github/workflows/backend-appservice.yml)

### What The Workflow Does

1. checks out the repository
2. installs backend dependencies
3. runs backend tests
4. logs into Azure using OpenID Connect
5. deploys the `backend/` package to Azure App Service

Current trigger mode:
- `workflow_dispatch` only

Why:
- prevents failed production deploy attempts before Azure secrets and app settings are ready
- keeps the first hosted deployment controlled

Later:
- once Azure resources and GitHub secrets are confirmed, this workflow can be expanded to deploy automatically on pushes to `main`

## GitHub Secrets Required

Set these repository secrets:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

These are used by `azure/login` with OpenID Connect.

## GitHub Variables Required

Set this repository variable:

- `AZURE_BACKEND_APP_NAME`

This should match the Azure App Service name for the backend.

## Azure Side Requirements

### Backend App Service
- Python runtime configured for the target version
- startup command set to:

```text
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Backend App Settings
- use [production-env-checklist.md](C:/Users/pc/Desktop/Pro_Jets/naija-sentiment-tracker/docs/production-env-checklist.md)
- keep:
  - `AUTO_CREATE_SCHEMA_ON_STARTUP=false`
  - `SCHEDULER_ENABLED=false`

## Frontend Deployment Recommendation

For Azure Static Web Apps, the recommended first path is:

1. create the Static Web App resource in Azure
2. connect it to the GitHub repository
3. let Azure generate the frontend workflow for the Static Web Apps deployment

Reason:
- Azure-generated Static Web Apps workflows are less error-prone than hand-writing the first one
- it keeps the backend App Service workflow and frontend Static Web Apps workflow aligned with Azure defaults

## First Release Rule

Before the backend workflow is allowed to publish to production:

1. Azure PostgreSQL must exist
2. production app settings must be configured
3. Alembic migrations must be applied
4. public read-only versus admin-only behavior must remain as documented in Week 8 prep
