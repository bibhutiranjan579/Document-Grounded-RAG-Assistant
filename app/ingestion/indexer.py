from pathlib import Path
from chromadb import Client
from chromadb.config import Settings

from app.config import CHROMA_DIR, DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from app.embeddings import get_encoder
from app.ingestion.chunker import create_chunks
from app.ingestion.loaders import load_document, list_documents


def build_or_load_collection(collection_name: str = "nexus_docs"):
    settings = Settings(persist_directory=str(CHROMA_DIR), is_persistent=True)
    chroma_client = Client(settings=settings)
    return chroma_client.get_or_create_collection(name=collection_name)


def index_documents(collection_name: str = "nexus_docs"):
    settings = Settings(persist_directory=str(CHROMA_DIR), is_persistent=True)
    chroma_client = Client(settings=settings)
    collection = chroma_client.get_or_create_collection(name=collection_name)

    chunks = []
    ids = []
    metadatas = []
    documents = []

    for path in list_documents(DATA_DIR):
        text = load_document(path)
        doc_chunks = create_chunks(path.name, text, CHUNK_SIZE, CHUNK_OVERLAP)
        for chunk in doc_chunks:
            ids.append(chunk["chunk_id"])
            metadatas.append({"document": chunk["document"]})
            documents.append(chunk["text"])
            chunks.append(chunk)

    if collection.count() > 0:
        return collection, chunks

    embeddings = encoder.encode(documents, convert_to_numpy=True).tolist()
    collection.add(
        ids=ids,
        metadatas=metadatas,
        documents=documents,
        embeddings=embeddings,
    )
    return collection, chunks
