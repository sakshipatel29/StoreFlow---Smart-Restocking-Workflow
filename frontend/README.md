# StoreFlow Frontend v4 — Production Deployment

This frontend is configured for the public StoreFlow FastAPI service:

```text
https://storeflow-api-0h7y.onrender.com/api/v1
```

## Public demo login

```text
Email:    admin@storeflow.demo
Password: StoreFlowDemo#2026Secure!
```

The demo login is intentionally public for recruiters and portfolio reviewers. It is not the Neon database password.

Before using this frontend, set the Render backend environment variable to the same value:

```text
DEMO_ADMIN_PASSWORD=StoreFlowDemo#2026Secure!
```

Then redeploy the backend so the seed script updates the demo account password.

## Local preview

```bash
python3 -m http.server 4173
```

Open `http://localhost:4173`.

## Render static-site settings

- Service type: Static Site
- Root Directory: `frontend`
- Build Command: `echo "No build required"`
- Publish Directory: `.`

After Render creates the frontend URL, add that exact HTTPS URL to the backend `CORS_ORIGINS` environment variable.
