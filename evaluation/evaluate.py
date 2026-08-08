import json
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.generation.llm import generate_answer
from app.ingestion.indexer import index_documents
from app.retrieval.bm25 import train_bm25, score_query
from app.retrieval.vector_search import search_vectors
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.reranker import rerank_candidates

BASE_DIR = Path(__file__).resolve().parent.parent

def load_questions(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate():
    collection, all_chunks = index_documents()
    bm25_model = train_bm25(all_chunks)
    questions = load_questions(BASE_DIR / "evaluation" / "questions.json")

    results = []
    found_count = 0
    total_latency = 0

    print("================================================")
    print("RAG Evaluation")
    print("================================================")

    for idx, item in enumerate(questions, start=1):
        question = item["question"]
        expected_source = item["expected_source"]
        start = time.time()
        bm25_results = score_query(bm25_model, question, all_chunks, top_n=15)
        vector_results = search_vectors(question, top_n=15)
        fused = reciprocal_rank_fusion([bm25_results, vector_results], top_k=20)
        reranked = rerank_candidates(question, fused, top_n=5)
        latency = int((time.time() - start) * 1000)
        total_latency += latency
        source_documents = [item["document"] for item in reranked]
        found = expected_source in source_documents
        if found:
            found_count += 1

        top_source = reranked[0]["document"] if reranked else None
        top_score = reranked[0]["rerank_score"] if reranked else 0.0

        results.append({
            "question": question,
            "expected_source": expected_source,
            "retrieval": "PASS" if found else "FAIL",
            "retrieved_sources": source_documents,
            "top_source": top_source,
            "top_score": float(top_score),
            "latency_ms": latency,
            "answer": "",
            "chunks": [
                {
                    "document": chunk["document"],
                    "chunk_id": chunk["chunk_id"],
                    "score": float(chunk["rerank_score"]),
                    "text": chunk["text"],
                }
                for chunk in reranked
            ],
        })

        print(f"Question {idx}")
        print(f"  question: {question}")
        print(f"  expected source: {expected_source}")
        print(f"  retrieval: {'PASS' if found else 'FAIL'}")
        print(f"  retrieved sources: {sorted(source_documents)}")
        print("  top reranked chunks:")
        for chunk in reranked:
            snippet = chunk["text"].replace("\n", " ")[:180].strip()
            print(
                f"    - {chunk['document']} | {chunk['chunk_id']} | score={chunk['rerank_score']:.4f} | {snippet}"
            )

        try:
            answer = generate_answer(question, reranked)
            print(f"  generated answer:\n    {answer.replace('\n', '\n    ')}")
            results[-1]["answer"] = answer
        except Exception as exc:
            print(f"  generated answer: SKIPPED ({exc})")
            results[-1]["answer"] = f"SKIPPED ({exc})"

        print(f"  latency_ms: {latency}\n")

    recall = found_count / len(questions)
    average_latency = int(total_latency / len(questions)) if questions else 0

    print("================================================")
    print(f"Retrieval Recall: {recall:.2f}")
    print(f"Average Latency: {average_latency} ms")

    return {
        "summary": {
            "total_questions": len(questions),
            "passed": found_count,
            "failed": len(questions) - found_count,
            "retrieval_recall": recall,
            "average_latency_ms": average_latency,
        },
        "results": results,
    }

if __name__ == "__main__":
    evaluate()
