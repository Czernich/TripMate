# TripMate

> **Type:** Long-term backend training project
> **Main stack:** Python + FastAPI

TripMate is a backend application for planning group trips.

The project is developed incrementally and is intended to simulate work on a real commercial backend system. New requirements, integrations, technical problems, and architectural decisions will appear over time, the same way they would in a real product team.

The project uses PostgreSQL for persistence, SQLAlchemy for database access, and Alembic for schema migrations. Authentication, authorization, and external integrations are planned for later stages.

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

Data is currently stored in PostgreSQL.

- PostgreSQL
- SQLAlchemy
- Alembic

## Infrastructure

Docker and Docker Compose are used for local development. See [Docker](#docker) for details.

## Testing

- pytest

## Code Quality

- Ruff
- mypy
- Bandit
- pre-commit

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
│   └── modules/            # Business logic, organized per domain module
│       └── trips/          # Trip domain: schemas, services, rules
│           └── schemas.py  # TripCreate, TripDetail and validation
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
    SQLAlchemy ORM models defining database tables.

app/modules/
    Application/business logic, grouped by domain (e.g. modules/trips/,
    modules/expenses/). Each module contains the services, schemas and rules
    for its own area, independent of the HTTP layer. Pydantic request/response
    schemas and business rule validation for a domain live in that domain's
    module (e.g. modules/trips/schemas.py), close to the logic they support.
```

---

# Requirements

## Required

- Python 3.14+
- Git

## Optional

- Docker & Docker Compose (see [Docker](#docker))
- Make for the `make` commands
- Bruno for running the API collection

---

# Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/Czernich/TripMate.git
cd TripMate
```

## 2. Run with Docker Compose

Copy the environment template:

```bash
cp .env.example .env
```

Build the application image, apply migrations, and start the application:

```bash
make migrate
make up
```

`make migrate` builds the application image and starts the database
before applying migrations.

The API is available at http://localhost:8000.

Stop the environment:

```bash
make down
```

## 3. Run locally without Docker

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
```

## 4. Install dependencies

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

## 5. Manage dependencies

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

## 6. Configure environment

Copy `.env.example` to `.env` and adjust values as needed. See [Environment Variables](#environment-variables) for details.

## 7. Start required services

If running without Docker Compose, you'll need PostgreSQL running separately, or use the Docker Compose flow above.

## 8. Run the application

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

SQLAlchemy ORM models are defined in `app/models/`.
Asynchronous database sessions are configured in `app/database.py`.

## Migrations

Alembic uses the database settings from `app.settings.settings_db`.
Migration commands run through Docker Compose using the Makefile.

Apply pending migrations:

```bash
make migrate
```

After updating SQLAlchemy models, generate a migration:

```bash
make migration message="describe schema change"
```

The generated file is saved locally in `alembic/versions/`.
Review its `upgrade()` and `downgrade()` functions, then `make migrate`.


Check the current database revision:

```bash
make current-revision
```

Show migration history:

```bash
make migration-history
```

Models are imported in `app/models/__init__.py`. Register new models there

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

The Makefile provides shortcuts for common development tasks:

- `make init` — copy `.env.example` to `.env`, install pre-commit hooks, and update pip-tools; requires local Python and pre-commit
- `make deps-compile` — compile `requirements.in` to `requirements.txt`
- `make deps-sync` — sync the local virtual environment with `requirements.txt`
- `make setup` — build the application image
- `make up` — start the application and its database
- `make down` — stop and remove the Compose containers
- `make logs` — follow application logs
- `make restart` — recreate the application environment

This avoids long CLI commands and keeps the workflow consistent across the team.

# Running Tests

## All tests

```bash
pytest
```

Tests reset the database schema only when `TESTING=true` and the database name
ends with `_test`. Running pytest with the regular `.env` is rejected to avoid
accidentally modifying the development database.

## API testing with Bruno

Open `tests_api/bruno` as a collection in Bruno and select the `local`
environment. Start the application and apply migrations before sending
requests.

Run the health checks first, then Create trip followed by Get created trip.
The create response supplies `tripId` automatically.
Run negative examples separately.

Only run requests implemented in the application version being tested.
Pagination, PATCH, and DELETE requests are not yet verified.
Successful create requests currently leave records in the database.

See the collection documentation for details and pending scenarios.



## Tests with Docker Compose

```bash
docker compose run --build --rm trip_mate_tests
```

Compose starts `db_tests` automatically. The test runner uses `.env.test`
and recreates the test schema before each test. The development database
is not used.

The test database has no volume, so it doesn't store any data. The test database schema is also recreated before every test.

## Testing Strategy

Tests cover health checks, schema validation, models, repositories,
services, and dependencies. Trip endpoint tests are added alongside
their implementations.

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
| `app/modules` | Application/business logic, per domain (e.g. trips), including domain schemas and validation |
| `app/exceptions` | Exception hierarchy (`base.py`) and global error handlers (`handlers.py`) |

---

# Error Handling

The application uses custom exception handling hierarchy extending `AppBaseException`. Errors raised within domain services are caught and returned as structured HTTP responses.

## Custom Exceptions Standard

All custom application errors share a uniform structure:
* **`status_code`**: Corresponding HTTP status code.
* **`error_code`**: Machine-readable string identifier for API clients.
* **`message`**: Human-readable error description.

| Exception | HTTP Status | Error Code | Default Message |
|---|---|---|---|
| `AppBaseException` | `500 Internal Server Error` | `INTERNAL_SERVER_ERROR` | An unexpected server error occurred. |
| `TripNotFoundException` | `404 Not Found` | `TRIP_NOT_FOUND` | Trip not found. |
| `TripAlreadyExistsException` | `409 Conflict` | `TRIP_ALREADY_EXISTS` | Trip already exists. |
| `TripUnprocessableException` | `422 Unprocessable Entity` | `TRIP_UNPROCESSABLE` | The trip cannot be edited in its current state. |
| `TripFullException` | `400 Bad Request` | `TRIP_IS_FULL` | Trip is fully booked. |

## API Error Format

Every error response uses the same JSON shape:

```json
{
  "error": {
    "code": "TRIP_NOT_FOUND",
    "message": "Trip with id 42 was not found."
  }
}
```

Validation errors (`422`, code `VALIDATION_ERROR`) additionally contain a `details` list with the Pydantic errors:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request payload.",
    "details": [
      {
        "type": "int_parsing",
        "loc": ["path", "trip_id"],
        "msg": "Input should be a valid integer, unable to parse string as an integer",
        "input": "abc"
      }
    ]
  }
}
```

Unhandled exceptions return `500` with a generic message. The stack trace is only written to the server log and is never sent to the client:

```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "Internal server error. Please try again later."
  }
}
```

## Domain Errors

Validation errors (empty trip name, invalid date range, invalid path parameter) return `422 Unprocessable Entity` with the `VALIDATION_ERROR` code. A non-existent trip returns `404 Not Found` with the `TRIP_NOT_FOUND` code.

## Code Layout

* `app/exceptions/base.py` - `AppBaseException`, the base class of all application exceptions.
* `app/exceptions/handlers.py` - exception handlers registered in `app/main.py` via `register_exception_handlers`.
* `app/modules/<domain>/exceptions.py` - domain-specific exceptions (e.g. trips).


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
