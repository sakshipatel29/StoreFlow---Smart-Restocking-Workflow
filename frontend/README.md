# StoreFlow Frontend v3 — Authenticated API Client

This frontend connects to StoreFlow Backend v2 and adds a complete login/session workflow.

## Included

- Portfolio-quality sign-in screen
- Demo credentials shown in the UI
- Bearer token added to every protected API request
- Token stored in `sessionStorage`, not persistent browser storage
- Current user displayed in the top bar
- Sign-out button
- Admin-only **Reset demo data** action
- Authenticated purchase-order CSV downloads
- Existing dashboard, product, inventory, sales, reorder, and purchase-order workflows

## Requirements

StoreFlow Backend v2 must be running at:

```text
http://localhost:8001
```

## Run

```bash
cd storeflow-frontend-v3-auth
python3 -m http.server 4173
```

Open:

```text
http://localhost:4173
```

Perform a hard refresh after replacing the previous frontend:

```text
Command + Shift + R
```

## Login

```text
Email:    admin@storeflow.demo
Password: StoreFlow123!
```

## Verify the session

1. Sign in.
2. Refresh the browser. You should remain signed in within that tab.
3. Open a second new tab manually. It receives its own tab session.
4. Select the sign-out icon. The protected application should disappear.
5. Sign in again and use **Reset demo data** to restore the original portfolio dataset.

## API configuration

Edit `config.js` only when the backend address changes:

```javascript
window.STOREFLOW_CONFIG = {
  apiBase: "http://localhost:8001/api/v1",
};
```
