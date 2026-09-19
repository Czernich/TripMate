.PHONY: setup down up logs restart

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
