from rank_bm25 import BM25Okapi
from typing import List, Dict


def train_bm25(chunks: List[Dict]) -> BM25Okapi:
    corpus = [chunk["text"].split() for chunk in chunks]
    return BM25Okapi(corpus)


def score_query(bm25_model: BM25Okapi, query: str, chunks: List[Dict], top_n: int = 15):
    tokenized = query.split()
    scores = bm25_model.get_scores(tokenized)
    ranked = sorted(
        [
            {
                "chunk_id": chunks[i]["chunk_id"],
                "document": chunks[i]["document"],
                "text": chunks[i]["text"],
                "score": float(scores[i]),
                "rank": i + 1,
            }
            for i in range(len(chunks))
        ],
        key=lambda item: item["score"],
        reverse=True,
    )
    return ranked[:top_n]
