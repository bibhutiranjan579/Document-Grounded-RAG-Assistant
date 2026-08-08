import threading
import time
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from app.models.schemas import (
    QueryRequest,
    QueryResponse,
    RetrieveResponse,
    RetrieveChunk,
    SourceItem,
    EvaluationResponse,
)
from app.ingestion.indexer import index_documents
from app.retrieval.bm25 import train_bm25, score_query
from app.retrieval.vector_search import search_vectors
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.reranker import rerank_candidates
from app.generation.llm import generate_answer

router = APIRouter()

_index_lock = threading.Lock()
_collection = None
_all_chunks = None
_bm25_model = None


def ensure_index():
    global _collection, _all_chunks, _bm25_model
    if _all_chunks is None or _bm25_model is None:
        with _index_lock:
            if _all_chunks is None or _bm25_model is None:
                _collection, _all_chunks = index_documents()
                _bm25_model = train_bm25(_all_chunks)
    return _collection, _all_chunks, _bm25_model

@router.get("/", summary="Service status")
def root():
    return {"status": "ok", "message": "ByteVox RAG API is running."}


@router.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    start = time.time()
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")

    _, all_chunks, bm25_model = ensure_index()
    bm25_results = score_query(bm25_model, request.question, all_chunks, top_n=15)
    vector_results = search_vectors(request.question, top_n=15)
    fused = reciprocal_rank_fusion([bm25_results, vector_results], top_k=20)
    reranked = rerank_candidates(request.question, fused, top_n=5)

    answer = generate_answer(request.question, reranked)
    sources = [
        SourceItem(
            document=item["document"],
            chunk_id=item["chunk_id"],
            score=item["rerank_score"],
            page=None,
        )
        for item in reranked
    ]
    latency_ms = int((time.time() - start) * 1000)
    return QueryResponse(answer=answer, sources=sources, latency_ms=latency_ms)


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve_endpoint(request: QueryRequest):
    start = time.time()
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")

    _, all_chunks, bm25_model = ensure_index()
    bm25_results = score_query(bm25_model, request.question, all_chunks, top_n=15)
    vector_results = search_vectors(request.question, top_n=15)
    fused = reciprocal_rank_fusion([bm25_results, vector_results], top_k=20)
    reranked = rerank_candidates(request.question, fused, top_n=5)

    chunks = [
        RetrieveChunk(
            document=item["document"],
            chunk_id=item["chunk_id"],
            score=item["rerank_score"],
            text=item["text"],
        )
        for item in reranked
    ]

    latency_ms = int((time.time() - start) * 1000)
    return RetrieveResponse(chunks=chunks, latency_ms=latency_ms)


@router.post("/evaluation/run", response_model=EvaluationResponse)
def evaluation_run():
    from evaluation.evaluate import evaluate as run_evaluation
    return run_evaluation()


@router.get("/dashboard")
def dashboard_redirect():
    return RedirectResponse(url="/static/index.html")
