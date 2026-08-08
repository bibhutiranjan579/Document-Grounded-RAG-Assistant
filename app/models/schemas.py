from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    question: str

class SourceItem(BaseModel):
    document: str
    chunk_id: str
    score: float
    page: Optional[int] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    latency_ms: int

class RetrieveChunk(BaseModel):
    document: str
    chunk_id: str
    score: float
    text: str

class RetrieveResponse(BaseModel):
    chunks: List[RetrieveChunk]
    latency_ms: int

class EvaluationSummary(BaseModel):
    total_questions: int
    passed: int
    failed: int
    retrieval_recall: float
    average_latency_ms: int

class EvaluationQuestionResult(BaseModel):
    question: str
    expected_source: str
    retrieval: str
    retrieved_sources: List[str]
    top_source: Optional[str]
    top_score: float
    latency_ms: int
    answer: str
    chunks: List[RetrieveChunk]

class EvaluationResponse(BaseModel):
    summary: EvaluationSummary
    results: List[EvaluationQuestionResult]
