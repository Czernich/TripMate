.PHONY: init deps-compile deps-sync setup down up logs restart alembic-revision alembic-upgrade alembic-current alembic-history

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

# Create an empty migration locally
alembic-revision:
	python -m alembic revision -m "$(message)"

# Build the app image and apply pending migrations
alembic-upgrade:
	docker compose run --build --rm trip_mate python -m alembic upgrade head

# Show the current database revision
alembic-current:
	docker compose run --rm trip_mate python -m alembic current

# Show available migration history
alembic-history:
	python -m alembic history