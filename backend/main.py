"""Main FastAPI application for clinical intelligence system."""

import asyncio
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import structlog

# On Windows, asyncio's default ProactorEventLoop can fail accept() with
# OSError(WinError 64), which silently destroys the listening socket: the process
# stays alive and keeps its memory, but the port stops accepting connections and
# the API appears frozen. The selector loop does not have this failure mode.
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except AttributeError:  # very old Python
        pass

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
    """Health probe that also reports retrieval readiness.

    Index coverage is included so a demo operator can see immediately whether the
    corpus and the FAISS/BM25 indexes are in sync.
    """
    corpus_docs = 0
    indexed_docs = 0
    try:
        if rag_service is not None:
            corpus_docs = len(rag_service._corpus)
            indexed_docs = len(set(rag_service.faiss._docs) | set(rag_service.bm25.doc_ids))
    except Exception:  # never let the health probe itself fail
        pass

    return {
        "status": "healthy",
        "model": settings.OPENROUTER_MODEL,
        "k_retrieve": settings.RAG_K_RETRIEVE,
        "k_rerank": settings.RAG_K_RERANK,
        "corpus_docs": corpus_docs,
        "indexed_docs": indexed_docs,
        "index_in_sync": corpus_docs == indexed_docs,
    }


if __name__ == "__main__":
    import uvicorn

    # loop="asyncio" + the selector policy above avoids the Windows accept() bug
    # that leaves the port bound but not listening.
    uvicorn.run(
        "backend.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
        loop="asyncio",
    )
