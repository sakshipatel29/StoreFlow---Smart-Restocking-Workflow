# Changelog

## v3 — Authentication

- Added sign-in screen and seeded demo credentials.
- Added bearer token handling for all FastAPI requests.
- Added current-user profile display and sign out.
- Added administrator demo reset control.
- Protected purchase-order exports.
- Changed token persistence to per-tab `sessionStorage`.
- Loaded `config.js` explicitly before `app.js`.

## v2 — API integration

- Replaced browser-only inventory storage with FastAPI and PostgreSQL.
