# TripMate

> **Type:** Long-term backend training project
> **Main stack:** Python + FastAPI

TripMate is a backend application for planning group trips.

The project is developed incrementally and is intended to simulate work on a real commercial backend system. New requirements, integrations, technical problems, and architectural decisions will appear over time, the same way they would in a real product team.

At this stage the repository contains a minimal, real REST API backed by in-memory storage. A persistent database, authentication, authorization, and external integrations will be introduced in later stages, once the product needs them.

The application, project structure, development environment, and this documentation are expected to evolve together with the product.

---


# About the Project

TripMate allows users to organize group trips.

A trip may eventually contain information such as:

- participants,
- destinations,
- itinerary,
- places to visit,
- expenses,
- expense settlements,
- budget,
- checklist,
- weather information,
- currency conversion,
- notifications.

Not all features are available from the beginning. Features are only implemented once they are introduced by a project ticket or requirement - see [Future Improvements](#future-improvements) for what is intentionally out of scope for now.

## Business Goal

TripMate solves the coordination problem of planning a trip with a group of people: who is going, where and when, what needs to be visited or done, who paid for what, and how the costs should be split. The primary users are small groups of friends or colleagues organizing a shared trip together.

The most important use cases at this stage are creating a trip and retrieving trip information through a REST API. Participants, expenses, and richer itinerary features are planned for subsequent stages (see the project's stage roadmap).

---

# Tech Stack

Update this section whenever a new technology becomes part of the project.

## Backend

- Python
- FastAPI
- Pydantic

## Database

Not introduced yet. Data is currently stored in memory. PostgreSQL + SQLAlchemy + Alembic are planned for a later stage.

## Infrastructure

Docker and Docker Compose are used for local development. See [Docker](#docker) for details.

## Testing

- pytest

## Code Quality

Not introduced yet. Ruff, mypy, and pre-commit are planned as part of the initial setup tasks.

---

# Project Structure

Document the actual repository structure. Do not design a large architecture in advance only because it may be useful later - the structure should evolve when the project requires it.

Example starting point:

```text
tripmate/
├── app/
│   ├── main.py            # FastAPI app instance and startup
│   ├── routes/             # HTTP layer - FastAPI routers and request/response schemas
│   ├── models/             # Domain / database models
│   └── modules/            # Business logic, organized per domain module (e.g. trips/, expenses/)
├── tests/
├── requirements.txt
└── README.md
```

## Directory Responsibilities

```text
app/routes/
    HTTP layer: FastAPI routers, request/response handling, and the Pydantic
    schemas used at the API boundary. Should stay thin and delegate real work
    to app/modules.

app/models/
    Domain and database models (Pydantic domain objects now; SQLAlchemy models
    once persistence is introduced).

app/modules/
    Application/business logic, grouped by domain (e.g. modules/trips/,
    modules/expenses/). Each module contains the services and rules for its
    own area, independent of the HTTP layer.
```

---

# Requirements

## Required

- Python 3.14+
- Git

## Optional

- Docker & Docker Compose (see [Docker](#docker))
- `make` (once the Makefile setup task is completed)

---

# Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/Czernich/TripMate.git
cd tripmate
```

## 2. Run with Docker Compose (recommended)

This starts both the API and a PostgreSQL database.

```bash
cp .env.example .env
docker compose up --build
```

The API will be available at `http://localhost:8000`, and PostgreSQL will be reachable on `localhost:5433` (mapped from the container's internal port 5432).

To stop and remove containers:

```bash
docker compose down
```

## 3. Run with Docker (API only, no database)

```bash
docker build -t trip_mate .
docker run -p 8000:8000 trip_mate
```

## 4. Run locally without Docker

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
```

## 5. Install dependencies

Install the pinned dependency management tools:

```bash
python -m pip install pip==26.2.1 pip-tools==7.6.1
```

Compile the dependency files:

```bash
pip-compile --output-file=requirements.txt requirements.in
pip-compile --output-file=requirements-dev.txt requirements-dev.in
```

Sync the virtual environment:

```bash
pip-sync requirements.txt requirements-dev.txt
```

## 6. Manage dependencies

`requirements.in` contains runtime dependencies and `requirements-dev.in` contains development dependencies.

All direct dependencies must be pinned to a specific version in the `.in` files.

`requirements.txt` and `requirements-dev.txt` are generated files and must not be edited manually.

### Runtime dependencies

Add a new dependency or update an existing version in `requirements.in`, then run:

```bash
pip-compile --output-file=requirements.txt requirements.in
pip-compile --output-file=requirements-dev.txt requirements-dev.in
```

### Development dependencies

Add a new dependency or update an existing version in `requirements-dev.in`, then run:

```bash
pip-compile --output-file=requirements-dev.txt requirements-dev.in
```

After changing dependencies, sync the environment using the command from the installation section.

## 7. Configure environment

Copy `.env.example` to `.env` and adjust values as needed. See [Environment Variables](#environment-variables) for details.

## 8. Start required services

If running without Docker Compose, you'll need PostgreSQL running separately, or use the Docker Compose flow above.

## 9. Run the application

```bash
uvicorn app.main:app --reload
```

---

# Environment Variables

Never commit secrets to the repository. Copy `.env.example` to `.env` and adjust values as needed.

| Variable | Required | Default | Description |
|---|---|---|---|
| `POSTGRES_USER` | Yes | - | PostgreSQL username |
| `POSTGRES_PASSWORD` | Yes | - | PostgreSQL password |
| `POSTGRES_DB` | Yes | - | PostgreSQL database name |

`.env` is listed in `.gitignore` and must never be committed.

---

# Running the Application

## Development

```bash
uvicorn app.main:app --reload
```

Expected local address:

```text
http://127.0.0.1:8000
```

## Production-like mode

```bash
docker compose up --build
```

---

# API Documentation

FastAPI automatically exposes OpenAPI documentation.

## Swagger UI

```text
http://127.0.0.1:8000/docs
```

## ReDoc

```text
http://127.0.0.1:8000/redoc
```

## OpenAPI schema

```text
http://127.0.0.1:8000/openapi.json
```

---

# API Endpoints

Keep a short overview of the main API resources. Detailed API contracts should remain available through OpenAPI.

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| POST | `/trips` | Create a new trip | None |
| GET | `/trips` | List all trips | None |
| GET | `/trips/{trip_id}` | Get a single trip by ID | None |

Example request body for `POST /trips`:

```json
{
  "name": "Barcelona Trip",
  "destination": "Barcelona",
  "start_date": "2026-09-10",
  "end_date": "2026-09-15"
}
```

---

# Database

## Database Engine

Connection pooling settings:

| Setting | Description |
|---|---|
| `pool_size` | Number of connections kept permanently open in the pool for the lifetime of the app process. |
| `max_overflow` | Maximum number of extra connections allowed above `pool_size`. |
| `pool_timeout` | How long a request waits for a free connection before SQLAlchemy raises a `TimeoutError` instead of hanging forever. |
| `pool_recycle` | Connections older than this value are closed and reopened, even if they are still healthy. |

## ORM

Not introduced yet. SQLAlchemy is planned for a later stage.

## Migrations

Database migrations are managed with Alembic. Connection settings are loaded
from environment variables through `app.settings.settings_db`.

Apply migrations:

```bash
docker compose run --rm trip_mate python -m alembic upgrade head
```

Check the current revision:

```bash
docker compose run --rm trip_mate python -m alembic current
```

Create an empty migration locally with the project's virtual environment activated:

```bash
python -m alembic revision -m "describe schema change"
```

Implement `upgrade()` and `downgrade()` in the generated file under
`alembic/versions/`, then rebuild the image and apply it:

```bash
docker compose build trip_mate
docker compose run --rm trip_mate python -m alembic upgrade head
```

Commit migration files to Git. The initial migration is an empty baseline.
Autogeneration will be enabled once SQLAlchemy model metadata is connected.

---

# External Integrations

Document every external system used by TripMate. Only document integrations that are actually introduced into the project.

Possible future integrations:

- weather providers,
- currency exchange APIs,
- geocoding services,
- country information APIs.

| Integration | Purpose | Documentation | Failure Strategy |
|---|---|---|---|
| - | - | - | None introduced yet |

---
## Using Makefile (recommended)

Once Docker and Docker Compose are introduced, the recommended way to interact with the project is through the Makefile.
It provides short, memorable commands for common developer tasks:

- make init — copy sample.env to .env, install pre-commit hooks, and update pip-tools
- make deps-compile — compile requirements.in to requirements.txt
- make deps-sync — sync local virtual environment with requirements.txt
- make setup — build the Docker image
- make up — start the environment
- make down — stop containers
- make logs — follow logs from all services
- make restart — restart the environment

This avoids long CLI commands and keeps the workflow consistent across the team.

# Running Tests

## All tests

```bash
pytest
```

Tests reset the database schema only when `TESTING=true` and the database name
ends with `_test`. Running pytest with the regular `.env` is rejected to avoid
accidentally modifying the development database.

## Tests with Docker Compose

Run the test database and test suite in containers. After the test run, remove
only the test containers. The development database and its `postgres_data`
volume are not affected:

```bash
(
   docker compose up --build trip_mate_tests db_tests

   docker compose rm trip_mate_tests db_tests

)
```

The test database has no volume, so it doesn't store any data. The test database schema is also recreated before every test.

## Testing Strategy

At this stage, tests cover the HTTP layer of the `/trips` endpoints, including basic validation rules (e.g. empty trip name, end date before start date, and requesting a non-existent trip). Unit tests for isolated business logic, database tests, and external API mocks will be added as those layers are introduced.

---

# Code Quality

## Code Quality & Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to run automated checks before every commit. This catches formatting issues, common security problems, and type errors before they reach the repository.

### Setup (one-time, after cloning)

```bash
pip install pre-commit
pre-commit install
```

This activates the Git hook locally. It only needs to be run once per clone.

### What runs on each commit

| Tool | Purpose |
|---|---|
| `pre-commit-hooks` | Basic hygiene: trailing whitespace, missing EOF newline, valid YAML, no large files, no accidentally committed private keys |
| [`ruff`](https://docs.astral.sh/ruff/) | Linting + auto-formatting for Python |
| [`mypy`](https://mypy.readthedocs.io/) | Static type checking |
| [`bandit`](https://bandit.readthedocs.io/) | Scans for common security issues in Python code |

Full configuration: [`.pre-commit-config.yaml`](.pre-commit-config.yaml)

### Running manually

Check all files (not just staged ones):
```bash
pre-commit run --all-files
```

Run a single hook:
```bash
pre-commit run mypy --all-files
```

### Updating hook versions

```bash
pre-commit autoupdate
```

---

# Docker

The project can be run fully containerized via Docker Compose, which starts both the API and a PostgreSQL database.

## Services

| Service | Description | Port |
|---|---|---|
| api | FastAPI backend | 8000 |
| db | PostgreSQL database (image: `postgres:18.6-trixie`) | 5433 (host) → 5432 (container) |

See [Getting Started](#getting-started) for usage instructions.

---

# Development Workflow

The project should be developed using a workflow similar to a commercial software project.

```text
Ticket
   ↓
Analysis
   ↓
Branch
   ↓
Implementation
   ↓
Tests
   ↓
Pull Request
   ↓
Code Review
   ↓
Fixes
   ↓
Merge
```

## General Rules

- Do not work directly on `master`.
- Each meaningful change should be connected to a ticket.
- Keep Pull Requests focused on one logical change.
- Add or update tests when behaviour changes.
- Do not merge code with failing tests.
- Do not commit secrets.
- Update documentation when setup or behaviour changes.
- Do not implement future requirements unless they are part of the current task.

---

# Branch Naming

Use a branch name connected to the ticket.

Recommended format:

```text
<TICKET-ID>-<short-description>
```

Example:

```text
TRIP-1-create-trip-endpoint
TRIP-23-add-weather-integration
TRIP-168-fix-duplicate-expenses
```

---

# Commit Convention

Example:

```text
TRIP-1: Add trip creation endpoint
TRIP-32: Add weather API client
TRIP-168: Fix duplicate expense creation
```

## Review Checklist

Before requesting review verify that:

- [ ] the application starts correctly,
- [ ] tests pass,
- [ ] new behaviour is covered by tests where appropriate,
- [ ] naming is understandable,
- [ ] unrelated changes are not included,
- [ ] no secrets were committed,
- [ ] README/documentation was updated if required.

---

# Architecture

This section should describe the architecture that **actually exists**. Do not document architecture that has not been implemented yet.

## Current Architecture

```text
Client
   |
   v
FastAPI
   |
   v
Application Logic (in-memory storage)
```

## Main Components

| Component | Responsibility |
|---|---|
| `app/routes` | HTTP layer - FastAPI routers, request/response handling and validation |
| `app/models` | Domain / database models |
| `app/modules` | Application/business logic, per domain (e.g. trips) |

---

# Error Handling

## API Error Format

```json
{
  "detail": "TODO"
}
```

Current format: FastAPI's default `{"detail": "..."}` shape for HTTP and validation errors. A more structured, consistent error-handling strategy is planned as one of the initial setup tasks.

## Domain Errors

Validation errors (empty trip name, invalid date range) currently return `422 Unprocessable Entity` via Pydantic validation. A non-existent trip returns `404 Not Found`.



# Future Improvements

- Trip participants and roles (Owner / Admin / Member / Viewer).
- Expense tracking and automatic balance calculation between participants.
- Persist data in PostgreSQL via SQLAlchemy and Alembic migrations.
- Authentication (registration, login, JWT access/refresh tokens).
- External integrations: weather, currency exchange, geocoding, country information.
- Caching with Redis once repeated external calls become a real problem.
- Docker/Docker Compose, CI/CD pipeline, and observability (logging, metrics, alerts).

---

# Development Principles

## Build only what is currently required

Do not implement functionality only because it may become useful later. Avoid unnecessary abstractions and premature optimization.

## Keep business logic outside the HTTP layer

FastAPI routers should primarily handle HTTP-related responsibilities. As the project grows, business rules should live in appropriate application/domain components.

## Tests are part of the implementation

A feature is not complete only because it works manually. Important business behaviour should be protected by automated tests.

## External systems can fail

Never assume that an external API always responds, responds quickly, returns valid data, or has unlimited request capacity.

## Refactoring is expected

The architecture created during the first weeks will not necessarily be the architecture used at the end of the project. Changing existing code as requirements grow is part of the exercise.


---

# Team

| Name                | Role            |
|---------------------|-----------------|
| Piotr Zegarek       | Project Manager |
| Igor Czernichowski  | Project Manager |
| Mateusz Ruszczyński | Developer       |
| Cezary Kulig        | Developer       |
| Anton Tsikhanovich  | Developer       |
| Tomasz Herman       | Developer       |
| Anita Gajewska      | Developer       |

---

# Important

This README is part of the project. It should evolve together with the codebase.

Whenever a change affects project setup, required services, environment variables, commands, architecture, API behaviour, or development workflow, consider whether this README should also be updated.

A developer joining the project should not need tribal knowledge to understand how to start working with TripMate.
