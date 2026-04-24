# Production Environment Checklist

Use this checklist when preparing Azure configuration for the first hosted deployment.

## Backend App Settings

Set these in the backend hosting environment.

### Required
- `APP_NAME=Naija Sentiment Tracker API`
- `APP_ENV=production`
- `API_V1_PREFIX=/api`
- `DATABASE_URL=<azure-postgresql-sqlalchemy-url>`
- `AZURE_LANGUAGE_ENDPOINT=<azure-language-endpoint>`
- `AZURE_LANGUAGE_KEY=<azure-language-key>`
- `AZURE_LANGUAGE_DEFAULT_LANGUAGE=en`
- `FRONTEND_ORIGIN=<deployed-frontend-origin>`

### Strongly Recommended
- `AUTO_CREATE_SCHEMA_ON_STARTUP=false`
- `SCHEDULER_ENABLED=false`
- `SCHEDULER_DAILY_HOUR=6`
- `SCHEDULER_INCLUDE_NEWS=true`
- `SCHEDULER_NEWS_LIMIT=20`
- `SCHEDULER_SKIP_NEWS_PAGES=true`
- `INGEST_BATCH_SIZE=10`
- `AZURE_LANGUAGE_BATCH_SIZE=10`
- `AZURE_LANGUAGE_RETRY_ATTEMPTS=3`
- `AZURE_LANGUAGE_RETRY_DELAY_SECONDS=2`
- `AZURE_LANGUAGE_BATCH_SLEEP_SECONDS=1`

### Only If Manual File Ingestion Is Still Used In Hosted Mode
- `CSV_SOURCE_PATH=<hosted-file-path-or-mounted-path>`

Note:
- If hosted file-based X ingestion is later replaced by an upload/admin flow, `CSV_SOURCE_PATH` may become a fallback rather than the primary operator path.

## Frontend App Settings

Set these in the frontend hosting environment.

### Required
- `NEXT_PUBLIC_API_BASE_URL=<deployed-backend-url>/api`

## Database Checklist

- Azure Database for PostgreSQL Flexible Server is provisioned
- firewall/network rules allow backend connectivity
- SSL/TLS requirements are reflected in the final connection string if needed
- Alembic migrations are ready to run against the Azure database

## Azure AI Checklist

- Azure AI Language resource exists
- endpoint and key are stored in backend app settings
- the chosen region and pricing tier are confirmed

## Public Vs Admin Checklist

### Public
- analysis page accessible
- operations page accessible if public-read-only remains the chosen policy
- no sign-in required for browsing

### Admin Only
- manual ingestion trigger
- future X upload/import path
- scheduler toggle

## First Deploy Recommended Values

- public dashboard: enabled
- admin actions: blocked until auth is implemented
- scheduler: disabled
- schema auto-create on startup: disabled
