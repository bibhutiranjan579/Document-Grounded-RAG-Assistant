import re
from typing import List, Dict


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    words = _clean_text(text).split(" ")
    if len(words) <= chunk_size:
        return [" ".join(words)]

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks


def create_chunks(document_name: str, content: str, chunk_size: int, overlap: int):
    chunks = chunk_text(content, chunk_size, overlap)
    return [
        {
            "document": document_name,
            "chunk_id": f"{document_name}__{i+1}",
            "text": chunk,
        }
        for i, chunk in enumerate(chunks)
    ]
