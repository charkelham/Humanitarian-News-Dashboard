# Humanitarian News Dashboard - Backend

FastAPI backend for Humanitarian News Dashboard platform.

## Setup

### Prerequisites
- Python 3.11+
- Poetry
- PostgreSQL 16 with pgvector extension

### Installation

1. Install dependencies:
```bash
poetry install
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run migrations:
```bash
alembic upgrade head
```

### Running Locally

```bash
uvicorn app.main:app --reload
```

Or with Docker:
```bash
docker-compose up backend
```

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

## Testing

Run all tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=app tests/
```

## Project Structure

```
backend/
├── app/
│   ├── api/           # API routes
│   ├── db/            # Database models & session
│   ├── models/        # Pydantic schemas
│   ├── services/      # Business logic
│   │   ├── ingest/    # RSS ingestion
│   │   ├── nlp/       # NLP enrichment
│   │   └── rag/       # RAG chatbot
│   ├── main.py        # FastAPI app
│   └── settings.py    # Configuration
├── alembic/           # Database migrations
├── tests/             # Test suite
└── pyproject.toml     # Dependencies
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
