.PHONY: setup down up logs restart

# Direct system setup: env file, pre-commit hooks, and python tools
init:
	cp -n sample.env .env || true
	pre-commit install
	python -m pip install --upgrade pip pip-tools

# Compile and sync python dependencies only
deps:
	pip-compile requirements.in
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
