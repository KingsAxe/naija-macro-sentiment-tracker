# Week 9 Deployment Notes

This file records the main Azure deployment issues encountered during Week 9, what each issue meant, and how it was resolved.

## Current Status

- Frontend deployment is live on Azure Static Web Apps.
- Backend GitHub Actions deployment is now succeeding after Azure identity and access fixes.
- Further hosted runtime validation should continue from this point.

## Key Issues Faced

### 1. Frontend Azure workflow generated with the wrong app path

What happened:
- Azure Static Web Apps generated a default workflow that pointed to the repository root.
- This repository is a monorepo, and the Next.js app lives under `frontend/`.

Impact:
- The generated workflow shape was not aligned with the actual frontend location.

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
- Replaced the hardcoded machine-specific path assertion with a backend-root-relative assertion that works across environments.

### 5. Azure login failed with `No subscriptions found`

What happened:
- GitHub OIDC was correctly reaching Azure.
- The app registration and federated credential were valid.
- However, the service principal used by GitHub Actions had no Azure role assignments.

Evidence:
- `az ad sp show --id <AZURE_CLIENT_ID>` returned the expected service principal.
- `az role assignment list --assignee <AZURE_CLIENT_ID> --all -o table` returned no rows.

Impact:
- `azure/login@v2` could not access the target subscription.
- Backend deployment could not proceed.

Resolution:
- Assigned Azure RBAC permissions to the correct GitHub Actions service principal.
- After the role assignment issue was fixed, the backend deployment workflow succeeded.

## Practical Lessons

- Confirm Azure role assignments with CLI instead of assuming the portal view is showing the correct principal.
- Avoid machine-specific absolute paths in tests that run in CI.
- Generated Azure workflows for monorepos usually need review before first use.
- Public project documentation should surface the live frontend, but should not unnecessarily expose internal backend service endpoints.

## Next Validation Work

- Verify hosted backend routes respond successfully.
- Verify frontend-to-backend connectivity with real deployed API responses.
- Run explicit cloud checks for:
  - `/api/health`
  - `/api/sentiment/summary`
  - `/operations`
- Confirm whether any hosted admin actions should remain blocked until authentication is completed.
