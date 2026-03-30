# 🌍 Humanitarian News Dashboard

A real-time humanitarian crisis monitoring platform built for analysts and policy professionals. The dashboard ingests articles from leading humanitarian sources, enriches them with NLP, and surfaces AI-generated situation briefs and a RAG-powered chat assistant.

---

## ✨ Features

- 📡 **Live ingestion** from OCHA, ReliefWeb, MSF, ICRC, Al Jazeera, BBC, Reuters and more
- 🗺️ **Country-filtered dashboard** — Sudan, Yemen, Gaza, DRC, Ethiopia, Somalia and 10+ more
- 🏷️ **NLP topic tagging** — conflict, displacement, famine, disease outbreak, natural disaster, and early warning
- 📰 **Topics feed** — filterable grid of articles by topic and country with timeline selector
- 🤖 **AI Situation Briefs** — GPT-4 powered analysis written for humanitarian professionals
- 💬 **RAG Chat Assistant** — ask questions about recent articles, grounded in your ingested data
- 🗄️ **pgvector semantic search** — embeddings stored in PostgreSQL for retrieval-augmented generation

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, SWR |
| Backend | FastAPI, Python 3.11, SQLAlchemy (async) |
| Database | PostgreSQL 16 + pgvector extension |
| AI | OpenAI GPT-4, text-embedding-ada-002 |
| Ingestion | RSS/Atom feeds, httpx, readability-lxml, BeautifulSoup |
| NLP | langdetect, custom topic classifier |
| Deployment | Docker, Railway |

---

## 📁 Project Structure

```
Humanitarian-News-Dashboard/
├── frontend/               # Next.js application
│   ├── app/
│   │   ├── page.tsx        # Main dashboard
│   │   ├── topics/         # Topics feed
│   │   ├── country-briefs/ # Country intelligence
│   │   └── feed-manager/   # Source management
│   └── components/
│       ├── Sidebar.tsx
│       └── ArticleChat.tsx # RAG chat component
└── backend/                # FastAPI application
    └── app/
        ├── api/            # REST endpoints
        ├── db/             # Models & session
        ├── models/         # Pydantic schemas
        └── services/
            ├── ingest/     # RSS ingestion & content extraction
            ├── nlp/        # Topic tagging & language detection
            └── rag/        # Chat & retrieval service
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+, Poetry
- Node.js 18+
- PostgreSQL 16 with [pgvector](https://github.com/pgvector/pgvector)
- OpenAI API key

### Backend

```bash
cd backend
poetry install
cp .env.example .env   # add your OPENAI_API_KEY and DATABASE_URL
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Or run everything with Docker:

```bash
docker-compose up
```

API docs available at `http://localhost:8000/docs`

---

## 📡 Key API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /articles` | Paginated article list with country/topic/date filters |
| `GET /articles/top-stories` | Ranked top stories for a country |
| `GET /briefs/latest` | Generate AI situation brief |
| `POST /chat` | RAG chat endpoint |
| `GET /stats/topic-breakdown` | Crisis type distribution |
| `GET /stats/activity` | Article activity over time |

---

## 🌐 Data Sources

OCHA · ReliefWeb · MSF · ICRC · Al Jazeera · BBC News · Reuters · The Guardian · UN News · Human Rights Watch · Amnesty International · France 24 · Deutsche Welle · AP News

---

## 📄 License

MIT