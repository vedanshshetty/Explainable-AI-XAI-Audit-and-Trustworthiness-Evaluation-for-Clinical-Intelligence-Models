"""Main FastAPI application for clinical intelligence system."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import structlog

from backend.app.config import settings
from backend.app.models import ClinicalCaseRequest
from backend.app.rag_service import RAGService

logger = structlog.get_logger(__name__)

rag_service: RAGService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_service
    logger.info("Starting clinical intelligence system")
    rag_service = RAGService()
    await rag_service.initialize()
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Clinical Intelligence System",
    description="Research-focused clinical decision support with XAI and trust evaluation",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Clinical Intelligence System", "version": "1.0.0", "docs": "/docs", "status": "operational"}


@app.post("/api/v1/analyze", response_model=dict)
async def analyze_case(payload: ClinicalCaseRequest):
    if rag_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        result = await rag_service.run_rag_pipeline(payload)
        return result.model_dump()
    except Exception as e:
        logger.error("Analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/status")
async def status():
    return {
        "status": "healthy",
        "model": settings.OPENROUTER_MODEL,
        "k_retrieve": settings.RAG_K_RETRIEVE,
        "k_rerank": settings.RAG_K_RERANK,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=settings.APP_DEBUG)
