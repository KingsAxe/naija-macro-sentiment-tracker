# Azure Release Runbook

This runbook defines the first recommended release flow for Azure deployment.

## Ordered Release Checklist

### 1. Provision Azure Core Services
- [ ] Create Azure Database for PostgreSQL Flexible Server
- [ ] Create Azure AI Language resource
- [ ] Create Azure App Service for the FastAPI backend
- [ ] Create Azure Static Web Apps for the frontend

### 2. Prepare GitHub Deployment Inputs
- [ ] Add GitHub secret `AZURE_CLIENT_ID`
- [ ] Add GitHub secret `AZURE_TENANT_ID`
- [ ] Add GitHub secret `AZURE_SUBSCRIPTION_ID`
- [ ] Add GitHub variable `AZURE_BACKEND_APP_NAME`

### 3. Configure Backend App Settings
- [ ] Apply values from [production-env-checklist.md](C:/Users/pc/Desktop/Pro_Jets/naija-sentiment-tracker/docs/production-env-checklist.md)
- [ ] Keep `AUTO_CREATE_SCHEMA_ON_STARTUP=false`
- [ ] Keep `SCHEDULER_ENABLED=false`
- [ ] Point `DATABASE_URL` to Azure PostgreSQL
- [ ] Point `FRONTEND_ORIGIN` to the deployed frontend URL

### 4. Configure Frontend App Settings
- [ ] Set `NEXT_PUBLIC_API_BASE_URL` to the deployed backend API base URL plus `/api`

### 5. Run Database Migrations Explicitly
- [ ] Run Alembic migrations against Azure PostgreSQL
- [ ] Verify the schema version matches `head`

Recommended command shape:

```powershell
cd backend
python -m alembic -c alembic.ini upgrade head
```

### 6. Deploy Backend
- [ ] Confirm Azure App Service startup command is:

```text
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- [ ] Trigger the GitHub Actions backend deployment workflow manually
- [ ] Verify the backend boots successfully
- [ ] Verify `/api/health` returns `ok`
- [ ] Verify `/api/sentiment/summary` responds successfully
- [ ] Verify backend connectivity to Azure PostgreSQL
- [ ] Verify backend connectivity to Azure AI Language

### 7. Deploy Frontend
- [ ] Connect Azure Static Web Apps to the GitHub repository
- [ ] Allow Azure to generate the frontend deployment workflow
- [ ] Verify the landing page loads
- [ ] Verify the operations page loads
- [ ] Verify the frontend can call deployed backend endpoints
- [ ] Verify there are no mixed-content or CORS issues

### 8. Enforce Public Vs Admin Boundary
- [ ] Confirm public users can browse the dashboard without signing in
- [ ] Confirm operator actions remain blocked until auth is added
- [ ] Keep hosted scheduler control disabled for public users
- [ ] Keep hosted manual ingestion blocked for public users

### 9. Run First Cloud Validation Cycle
- [ ] Verify backend health and API responses
- [ ] Verify dashboard data renders correctly
- [ ] Verify at least one hosted ingestion path
- [ ] Verify Azure AI results persist correctly
- [ ] Verify public pages remain readable without sign-in
- [ ] Verify admin actions are not publicly available

### 10. After First Successful Release
- [ ] Decide whether scheduler execution should stay in the API temporarily or move to an Azure-native job
- [ ] Implement admin authentication before exposing operational controls in the hosted environment
- [ ] Only then consider enabling hosted scheduler behavior
