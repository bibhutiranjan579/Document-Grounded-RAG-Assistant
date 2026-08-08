from openai import OpenAI
from typing import List, Dict
from app.config import OPENAI_API_KEY, OPENAI_MODEL


def _build_prompt(question: str, chunks: List[Dict]) -> str:
    context_sections = []
    for idx, chunk in enumerate(chunks, start=1):
        context_sections.append(
            f"Source {idx}: {chunk['document']} | Chunk {chunk['chunk_id']}\n{chunk['text']}"
        )
    context_text = "\n\n".join(context_sections)
    return (
        "You are a document-grounded assistant. Answer the user's question using ONLY the provided context. "
        "If the answer cannot be found in the context, say so clearly and do not invent information. "
        "Do not include unrelated text.\n\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {question}\n"
    )


def generate_answer(question: str, chunks: List[Dict]) -> str:
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not configured. Set OPENAI_API_KEY in the environment.")
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = _build_prompt(question, chunks)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that cites only the provided sources."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=320,
        temperature=0.2,
    )
    message = response.choices[0].message
    if isinstance(message, dict):
        return message["content"].strip()
    return getattr(message, "content", "").strip()
