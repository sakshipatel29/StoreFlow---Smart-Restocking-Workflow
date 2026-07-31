.PHONY: install run migrate seed reset-seed test lint up down logs

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --reload --port 8000

migrate:
	alembic upgrade head

seed:
	python -m app.scripts.seed

reset-seed:
	python -m app.scripts.seed --reset

test:
	pytest -q

lint:
	ruff check .

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f api
