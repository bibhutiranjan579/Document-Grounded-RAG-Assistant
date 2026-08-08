import numpy as np
from typing import List, Dict
from app.embeddings import get_encoder


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def rerank_candidates(question: str, candidates: List[Dict], top_n: int = 5) -> List[Dict]:
    question_embedding = get_encoder().encode(question, convert_to_numpy=True)
    texts = [candidate["text"] for candidate in candidates]
    embeddings = get_encoder().encode(texts, convert_to_numpy=True)

    reranked = []
    for candidate, embedding in zip(candidates, embeddings):
        similarity = _cosine_similarity(question_embedding, embedding)
        score = similarity + 0.15 * candidate.get("score", 0.0)
        reranked.append({**candidate, "rerank_score": score, "similarity": similarity})

    reranked_sorted = sorted(reranked, key=lambda item: item["rerank_score"], reverse=True)
    return reranked_sorted[:top_n]
