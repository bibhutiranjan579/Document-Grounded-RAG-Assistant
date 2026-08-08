from app.embeddings import get_encoder
from app.ingestion.indexer import build_or_load_collection
from typing import List, Dict


def search_vectors(query: str, top_n: int = 15) -> List[Dict]:
    collection = build_or_load_collection()
    query_embedding = get_encoder().encode(query, convert_to_numpy=True).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_n,
        include=["metadatas", "documents", "distances"],
    )
    hits = []
    for i in range(len(results["ids"][0])):
        hits.append(
            {
                "chunk_id": results["ids"][0][i],
                "document": results["metadatas"][0][i]["document"],
                "text": results["documents"][0][i],
                "score": float(results["distances"][0][i]),
                "rank": i + 1,
            }
        )
    return hits
