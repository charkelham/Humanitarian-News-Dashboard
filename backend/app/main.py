"""
FastAPI application entry point for SENTINEL humanitarian intelligence backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ingestion, chat, articles, countries, sources, briefs, stats, admin

app = FastAPI(
    title="Humanitarian News Dashboard",
    description="Early warning RSS ingestion, crisis classification and RAG chatbot for FCDO/HEROS humanitarian monitoring",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(ingestion.router)
app.include_router(chat.router)
app.include_router(articles.router)
app.include_router(countries.router)
app.include_router(sources.router)
app.include_router(briefs.router)
app.include_router(stats.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "SENTINEL API"}


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": "SENTINEL Humanitarian Intelligence",
        "version": "1.0.0"
    }