.PHONY: help up down logs restart ps migrate test shell db-shell clean

help:
	@echo "Humanitarian News Dashboard - Makefile Commands"
	@echo "========================================="
	@echo "up          - Start all services (detached)"
	@echo "down        - Stop and remove all containers"
	@echo "logs        - Follow logs from all services"
	@echo "logs-backend - Follow backend logs only"
	@echo "logs-worker  - Follow worker logs only"
	@echo "restart     - Restart all services"
	@echo "ps          - Show running containers"
	@echo "migrate     - Run database migrations"
	@echo "test        - Run backend tests"
	@echo "ingest-now  - Trigger manual ingestion run"
	@echo "shell       - Open backend container shell"
	@echo "db-shell    - Open PostgreSQL shell"
	@echo "clean       - Remove containers, volumes, and images"

up:
	docker-compose up -d
	@echo "Services started! Backend: http://localhost:8000 | Frontend: http://localhost:3000"

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

ps:
	docker-compose ps

migrate:
	docker-compose exec backend alembic upgrade head

test:
	docker-compose exec backend pytest tests/ -v

logs-backend:
	docker-compose logs -f backend

logs-worker:
	docker-compose logs -f worker

ingest-now:
	docker-compose exec backend python -m app.ingest.run_once

shell:
	docker-compose exec backend /bin/bash

db-shell:
	docker-compose exec postgres psql -U hnd_user -d hnd_db

clean:
	docker-compose down -v --rmi local
	@echo "Cleaned up containers, volumes, and images"
