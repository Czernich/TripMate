.PHONY: init deps-compile deps-sync setup down up logs restart migration migrate current-revision migration-history

# Direct system setup: env file, pre-commit hooks, and python tools
init:
	@test -f .env || cp sample.env .env
	pre-commit install
	python3 -m pip install --upgrade pip pip-tools

# Compile requirements.in -> requirements.txt (only when dependencies change)
deps-compile:
	pip-compile requirements.in

# Sync local virtual environment with requirements.txt
deps-sync:
	pip-sync requirements.txt

# Built docker image
setup:
	docker build -t trip_mate .

# Stop docker compose
down:
	docker compose down

# Start docker compose in detached mode
up:
	docker compose up -d

# Follow logs from app container
logs:
	docker compose logs -f trip_mate

# Restart all containers
restart:
	docker compose down && docker compose up -d

# Generate a migration from model changes
migration:
	docker compose run --build --rm trip_mate python -m alembic revision --autogenerate -m "$(message)"

# Build the app image and apply pending migrations
migrate:
	docker compose run --build --rm trip_mate python -m alembic upgrade head

# Show the current database revision
current-revision:
	docker compose run --rm trip_mate python -m alembic current

# Show migration history
migration-history:
	docker compose run --rm trip_mate python -m alembic history
