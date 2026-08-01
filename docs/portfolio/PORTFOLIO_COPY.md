# StoreFlow Portfolio Copy

## Portfolio title

**StoreFlow — Smart Restocking Workflow**

## Subtitle

A Forward Deployed Engineering project that converts convenience-store sales and inventory activity into explainable reorder recommendations and supplier-specific purchase orders.

## Problem

A convenience-store owner manually checks shelves and prepares separate supplier orders every week because the existing billing workflow does not maintain reliable SKU-level inventory. This makes ordering repetitive, difficult to audit, and dependent on memory.

## Solution

I designed and deployed StoreFlow, a full-stack inventory workflow that validates product-level sales, maintains an auditable inventory ledger, identifies stock risk, produces explainable case-based reorder recommendations, and manages purchase orders from review through delivery receiving.

## What I built

- FastAPI and PostgreSQL backend with SQLAlchemy and Alembic migrations
- Authenticated inventory, sales, recommendation, analytics, and purchase-order APIs
- CSV sales ingestion with validation, barcode matching, and invalid-row handling
- Explainable reorder engine using demand history, lead time, safety stock, and case sizes
- Human approval workflow for recommendation changes and supplier-specific orders
- Static web interface connected to the deployed API
- Docker Compose development environment, Pytest coverage, and GitHub Actions CI
- Public deployment using Render and Neon PostgreSQL
- Resettable synthetic demo with 48 products and 4,067 sales records

## Links

Live demo:
https://storeflow-smart-restocking-workflow.onrender.com/

GitHub:
https://github.com/sakshipatel29/StoreFlow---Smart-Restocking-Workflow

## Demo credentials

Email: admin@storeflow.demo  
Password: StoreFlowDemo#2026Secure!

## Role relevance

StoreFlow demonstrates customer discovery, legacy-workflow adaptation, data modeling, backend engineering, explainability, deployment, testing, and communication with a nontechnical stakeholder—the core combination expected in Forward Deployed Engineering roles.

## Honest impact wording

Use this before a real pilot:

> Designed and deployed a pilot-ready restocking workflow based on a real convenience-store ordering process.

Use this only after measuring it:

> Reduced weekly order preparation from X minutes to Y minutes and achieved Z% owner acceptance of automated reorder recommendations during a pilot covering N products.
