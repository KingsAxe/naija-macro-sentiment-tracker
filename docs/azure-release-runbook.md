# Azure Release Runbook

This runbook defines the first recommended release flow for Azure deployment.

## 1. Provision Core Services

- Azure Static Web Apps for the frontend
- Azure App Service for the FastAPI backend
- Azure Database for PostgreSQL Flexible Server
- Azure AI Language resource

## 2. Configure Environment Values

### Backend
- apply the values from [production-env-checklist.md](C:/Users/pc/Desktop/Pro_Jets/naija-sentiment-tracker/docs/production-env-checklist.md)
- keep:
  - `AUTO_CREATE_SCHEMA_ON_STARTUP=false`
  - `SCHEDULER_ENABLED=false`

### Frontend
- set `NEXT_PUBLIC_API_BASE_URL` to the deployed backend API base

## 3. Prepare Database Release Step

Before the backend is considered live:

1. point the backend environment to the Azure PostgreSQL instance
2. run Alembic migrations explicitly
3. verify the schema version matches `head`

Recommended command shape:

```powershell
cd backend
python -m alembic -c alembic.ini upgrade head
```

## 4. Deploy Backend

Recommended startup command:

```text
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Backend release checks:
- app boots successfully
- `/api/health` returns `ok`
- `/api/sentiment/summary` returns successfully
- backend can reach Azure PostgreSQL
- backend can reach Azure AI Language

## 5. Deploy Frontend

Frontend release checks:
- landing page loads
- operations page loads
- frontend can call deployed backend endpoints
- no mixed-content or CORS issues

## 6. Enforce Public Vs Admin Boundary

At first deployment:
- public users can browse the dashboard without signing in
- operator actions remain blocked until auth is added

Do not enable hosted scheduler control or hosted manual ingestion for public users before admin protection exists.

## 7. First Cloud Validation Cycle

Run one controlled validation cycle:

1. verify backend health and API responses
2. verify dashboard data renders correctly
3. verify at least one ingestion path in the hosted environment
4. verify Azure AI results are persisted correctly
5. verify public pages remain readable without sign-in
6. verify admin actions are not publicly available

## 8. After First Successful Release

Once the hosted environment is stable:
- decide whether scheduler execution should stay in the API temporarily or move to an Azure-native job
- implement admin authentication before exposing operational controls in the hosted environment
- then enable hosted scheduler behavior if still desired
