from typing import List, Dict


def reciprocal_rank_fusion(results: List[List[Dict]], top_k: int = 20, k: int = 60) -> List[Dict]:
    aggregate = {}
    for result_set in results:
        for rank, item in enumerate(result_set, start=1):
            chunk_id = item["chunk_id"]
            score = 1.0 / (k + rank)
            if chunk_id not in aggregate:
                aggregate[chunk_id] = {
                    "chunk_id": chunk_id,
                    "document": item["document"],
                    "text": item["text"],
                    "score": 0.0,
                    "source_ranks": [],
                }
            aggregate[chunk_id]["score"] += score
            aggregate[chunk_id]["source_ranks"].append(rank)

    ranked = sorted(aggregate.values(), key=lambda item: item["score"], reverse=True)
    for idx, item in enumerate(ranked, start=1):
        item["rank"] = idx
    return ranked[:top_k]
