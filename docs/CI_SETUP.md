# StoreFlow GitHub Actions CI

This workflow validates StoreFlow automatically whenever code is pushed to `main` or `develop`, and whenever a pull request is opened or updated.

## Checks included

1. **Backend tests**
   - Installs Python 3.12 and development dependencies.
   - Compiles the backend source.
   - Runs the complete Pytest suite using SQLite isolation.

2. **PostgreSQL smoke test**
   - Starts PostgreSQL 17 as a service container.
   - Runs all Alembic migrations.
   - Seeds the real StoreFlow dataset.
   - Verifies 4 suppliers, 48 products, 4,067 sales, and at least one user.

3. **Frontend checks**
   - Validates `app.js` and `config.js` syntax.
   - Starts the static frontend server.
   - Confirms the main HTML, JavaScript, and CSS files are reachable.

4. **Docker build**
   - Builds the backend Docker image after backend tests pass.

## Install the files

From the root of the repository, copy the `.github` folder from this package into the repository root.

The result must look like this:

```text
StoreFlow---Smart-Restocking-Workflow/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
├── frontend/
└── ...
```

## Commit and push

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add full-stack GitHub Actions workflow"
git push origin main
```

Open the GitHub repository and select **Actions**. The workflow named **StoreFlow CI** should start automatically.

## Expected jobs

```text
Backend tests                  passed
PostgreSQL migration and seed  passed
Frontend checks                passed
Backend Docker build           passed
```

## Optional README badge

Replace `YOUR_USERNAME` and `YOUR_REPOSITORY`:

```markdown
[![StoreFlow CI](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/actions/workflows/ci.yml)
```

## Troubleshooting

### Workflow cannot find `backend`

The workflow assumes `.github`, `backend`, and `frontend` are all inside the same repository root. Move `.github` to the root rather than placing it inside `backend`.

### Pytest is not installed

Confirm `backend/requirements-dev.txt` contains:

```text
-r requirements.txt
pytest>=8,<10
httpx>=0.27,<1.0
ruff>=0.8,<1.0
```

### PostgreSQL job cannot connect

Do not change the CI database host to `db`. GitHub Actions runs the job directly on the runner, so its PostgreSQL service is reached through `localhost:5432`.

### Seed count fails

Reset accidental changes to the CSV files under `backend/data`, or update the assertion only when the intended demo dataset has changed.
