# StoreFlow Authentication Flow

```text
Login form
   ↓ POST /api/v1/auth/login
Verify scrypt password hash
   ↓
Create signed, expiring bearer token
   ↓
Frontend stores token in sessionStorage
   ↓ Authorization: Bearer <token>
Protected FastAPI route
   ↓
Validate signature, expiration, user, and active status
   ↓
Execute inventory/order operation
```

## Design decisions

- `sessionStorage` limits the demo token to the current browser tab.
- Passwords are never stored directly; only salted `scrypt` hashes are persisted.
- All operational routes are protected at the router level, reducing the chance that a new route is accidentally public.
- The demo reset requires the `admin` role and preserves user accounts.
- This release remains single-store. Store-level authorization is the next evolution for a multi-tenant SaaS product.
