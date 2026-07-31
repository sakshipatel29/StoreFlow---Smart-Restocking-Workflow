# Deploy StoreFlow Frontend on Render

## 1. Use the production frontend files

Replace the repository's `frontend` directory with this folder's contents, or copy `config.js`, `app.js`, `index.html`, and `README.md` into it.

## 2. Align the public demo password

In the Render backend service, set:

```text
DEMO_ADMIN_PASSWORD=StoreFlowDemo2026!
```

Save and deploy. This password is intentionally public and is separate from the private Neon database password.

## 3. Commit the frontend

```bash
git add frontend
git commit -m "deploy: configure production frontend"
git push origin main
```

## 4. Create the static site

In Render:

1. New → Static Site
2. Connect the StoreFlow repository
3. Name: `storeflow-web`
4. Branch: `main`
5. Root Directory: `frontend`
6. Build Command: `echo "No build required"`
7. Publish Directory: `.`
8. Create Static Site

## 5. Add the frontend URL to backend CORS

After Render creates a URL such as:

```text
https://storeflow-web-xxxx.onrender.com
```

Open the backend Render service → Environment and set:

```text
CORS_ORIGINS=["http://localhost:4173","http://127.0.0.1:4173","https://storeflow-web-xxxx.onrender.com"]
```

Use your exact frontend URL, without a trailing slash. Save and redeploy the backend.

## 6. Verify

Open the frontend URL and sign in using:

```text
admin@storeflow.demo
StoreFlowDemo2026!
```

Test dashboard loading, inventory adjustment persistence, sales import, recommendation generation, purchase-order creation, and sign-out.
