# Week 9 Deployment Notes

This file records the main Azure deployment issues encountered during Week 9, what each issue meant, and how it was resolved.

## Final Week 9 Outcome

Week 9 cloud validation is complete.

Confirmed working at the end of Week 9:

- frontend deployment on Azure Static Web Apps
- backend deployment on Azure App Service
- Azure PostgreSQL connectivity
- Alembic migrations in the hosted environment
- manual X ingestion in Azure
- Vanguard and Punch news ingestion in Azure
- Azure AI Language sentiment analysis in Azure
- frontend runtime fetching against the hosted backend
- backend CORS configuration for the hosted frontend
- operations-page ingestion QA visibility

## Key Issues Faced

### 1. Frontend Azure workflow generated with the wrong app path

What happened:
- Azure Static Web Apps generated a default workflow that pointed to the repository root.
- This repository is a monorepo, and the Next.js app lives under `frontend/`.

Impact:
- The generated workflow was not aligned with the actual frontend location.

Resolution:
- Updated the Azure Static Web Apps workflow to build from `frontend/`.
- Added the `NEXT_PUBLIC_API_BASE_URL` GitHub Actions variable so the hosted frontend build can target the deployed backend API.

### 2. Backend App Service initially served the default Azure landing page

What happened:
- The App Service was reachable, but the deployed FastAPI application was not being started correctly.

Impact:
- Backend API routes such as `/api/health` were unavailable.

Resolution:
- Set the backend startup command in Azure App Service to:

```text
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Backend runtime failed with `No module named uvicorn`

What happened:
- Azure logs showed that App Service was attempting to run the startup command, but Python dependencies were not installed in the deployed environment.

Impact:
- The backend process could not start successfully.

Resolution:
- Added these Azure App Service settings:

```text
SCM_DO_BUILD_DURING_DEPLOYMENT=true
ENABLE_ORYX_BUILD=true
```

- This enabled dependency installation during deployment.

### 4. Backend GitHub Actions workflow failed on a brittle test

What happened:
- One ingestion test hardcoded a local Windows absolute path.
- GitHub Actions runs on Linux, so the assertion failed even though the logic was correct.

Impact:
- The backend deployment workflow stopped before reaching Azure deployment.

Resolution:
- Replaced the machine-specific path assertion with a backend-root-relative assertion that works across environments.

### 5. Azure login failed with `No subscriptions found`

What happened:
- GitHub OIDC was correctly reaching Azure.
- The app registration and federated credential were valid.
- However, the service principal used by GitHub Actions had no Azure role assignments.

Impact:
- `azure/login@v2` could not access the target subscription.
- Backend deployment could not proceed.

Resolution:
- Assigned Azure RBAC permissions to the correct GitHub Actions service principal.
- After the role assignment issue was fixed, the backend deployment workflow succeeded.

### 6. Static frontend deployment served stale zero-state data

What happened:
- The frontend initially relied on server/build-time data fetching, but the deployed app was hosted on Azure Static Web Apps Free.

Impact:
- The deployed frontend rendered stale empty-state HTML even when the backend contained real data.

Resolution:
- Moved the dashboard pages to runtime client-side fetching.
- Fixed `NEXT_PUBLIC_API_BASE_URL` injection in the frontend deployment workflow.

### 7. Hosted frontend calls were blocked by CORS until the frontend origin was aligned

What happened:
- The backend did not initially return the correct `Access-Control-Allow-Origin` header for the deployed frontend.

Impact:
- Hosted frontend requests to the backend failed in the browser.

Resolution:
- Set `FRONTEND_ORIGIN` in Azure App Service to the deployed frontend origin.
- Restarted the backend so FastAPI CORS middleware picked up the hosted origin.

## Practical Lessons

- Generated Azure workflows for monorepos should always be reviewed before first use.
- GitHub OIDC setup is not complete until the service principal has the correct Azure RBAC assignment.
- Azure Static Web Apps Free should be treated as a static hosting target, not a guaranteed hybrid SSR runtime.
- Runtime environment values for frontend builds must be validated in the deployed browser, not just in workflow YAML.
- Public repo docs should explain deployment at a high level without exposing sensitive operational details.

## Follow-On Work After Week 9

After cloud validation, the next areas of improvement are:

- news-topic taxonomy quality
- rejected-news QA visibility
- article-page fetch reliability for hosted sources
- opinion-mining yield on hosted news content
- safe automation of the full hosted ingestion pipeline
