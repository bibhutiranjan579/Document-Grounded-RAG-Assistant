# ByteVox RAG Assignment

## Project Overview

This project implements a document-grounded Retrieval-Augmented Generation (RAG) assistant for the Nexus AI Platform documentation.

The system ingests `.txt`, `.md`, and `.pdf` documents, splits them into overlapping chunks, indexes the chunks using vector embeddings and BM25, combines lexical and semantic retrieval using Reciprocal Rank Fusion (RRF), reranks the retrieved candidates, and generates grounded answers using the OpenAI API.

The system is exposed through a FastAPI REST API and includes:

- A retrieval-only endpoint for inspecting retrieved chunks
- An end-to-end RAG query endpoint for generating grounded answers
- An evaluation endpoint for running the benchmark
- An interactive evaluation dashboard
- Custom question testing through retrieval and full RAG generation

---

## Architecture

The RAG pipeline follows this flow:

    User Question
          |
          v
    FastAPI REST API
          |
    +-----+-----+
    |           |
    v           v
/retrieve     /query
    |           |
    +-----+-----+
          |
          v
    Hybrid Retrieval
      /         \
     /           \
    v             v
BM25 Search   Vector Search
    |             |
    +------+------+
           |
           v
 Reciprocal Rank Fusion
           |
           v
       Reranker
           |
           v
   Top Relevant Chunks
      /           \
     /             \
    v               v
Return Chunks   LLM Context
 (/retrieve)        |
                    v
               OpenAI API
                    |
                    v
             Answer + Sources

The retrieval pipeline is separated from LLM generation so that retrieval quality can be tested independently.

---

## Project Structure

    bytevox-rag-assignment/
    │
    ├── app/
    │   ├── api/
    │   ├── generation/
    │   ├── ingestion/
    │   ├── retrieval/
    │   ├── static/
    │   │   ├── index.html
    │   │   ├── styles.css
    │   │   └── app.js
    │   └── main.py
    │
    ├── data/
    │   └── documents/
    │
    ├── evaluation/
    │   ├── evaluate.py
    │   └── questions.json
    │
    ├── docs/
    │   ├── design.md
    │   └── architecture.png
    │
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    └── README.md

---

## Retrieval Pipeline

The system uses hybrid retrieval rather than relying only on semantic similarity.

### 1. Document Ingestion

The ingestion pipeline supports:

- PDF
- Markdown
- Plain text

Documents are loaded from:

    data/documents/

### 2. Chunking

Documents are divided into overlapping chunks before indexing.

The overlap helps preserve context when relevant information spans chunk boundaries.

### 3. Vector Retrieval

Each chunk is converted into an embedding using SentenceTransformers and stored in ChromaDB.

Vector retrieval is useful for finding semantically related content even when the query and document use different wording.

### 4. BM25 Retrieval

BM25 provides lexical retrieval based on keyword matching.

This is particularly useful for technical queries containing:

- API endpoint names
- Configuration parameters
- Error codes
- Product terminology
- Exact technical terms

### 5. Reciprocal Rank Fusion

Results from BM25 and vector retrieval are combined using Reciprocal Rank Fusion (RRF).

This allows the system to benefit from both lexical and semantic retrieval.

### 6. Reranking

The fused candidates are reranked using semantic relevance scores before the final context is passed to the LLM.

### 7. Grounded Generation

The highest-ranked chunks are provided to the LLM as context.

The generation prompt instructs the model to answer using the supplied documentation and avoid unsupported information.

---

## Tech Stack

- Python 3.13
- FastAPI
- Uvicorn
- ChromaDB
- SentenceTransformers
- rank-bm25
- OpenAI Python SDK 2.x
- python-dotenv
- PyMuPDF (`pymupdf`)
- Pydantic
- HTML
- CSS
- JavaScript

---

## Setup

### 1. Clone the repository

    git clone <your-github-repository-url>
    cd bytevox-rag-assignment

### 2. Create a virtual environment

    python3 -m venv venv
    source venv/bin/activate

### 3. Install dependencies

    pip install -r requirements.txt

### 4. Configure environment variables

Create a `.env` file in the project root:

    OPENAI_API_KEY="your-openai-api-key"
    OPENAI_MODEL="your-configured-model"

Do not commit `.env` to GitHub.

A `.env.example` file is included as a template.

---

## Document Ingestion

Document ingestion happens automatically when the API starts or when the evaluation script runs.

- Source documents are read from `data/documents`
- Chunks are created with overlapping windows
- Embeddings are generated using SentenceTransformers
- Embeddings are stored in the local ChromaDB directory: `.chromadb`
- BM25 indexes are built for lexical retrieval

If `.chromadb` already contains indexed data, the system reuses the existing collection.

---

## Running the API

Start the FastAPI service with Uvicorn:

    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

The API will be available at:

    http://localhost:8000

The interactive evaluation dashboard is available at:

    http://localhost:8000/dashboard

Interactive Swagger API documentation is available at:

    http://localhost:8000/docs

---

## Available Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/retrieve` | Retrieve and rerank relevant document chunks without calling the LLM |
| POST | `/query` | Run the complete RAG pipeline and generate a grounded answer |
| POST | `/evaluation/run` | Run the benchmark evaluation suite and return retrieval metrics |
| GET | `/dashboard` | Open the interactive evaluation dashboard |

---

# Dashboard and Evaluation

A lightweight interactive evaluation dashboard is available at:

    http://localhost:8000/dashboard

The dashboard provides:

- One-click benchmark evaluation using `/evaluation/run`
- Retrieval-only testing using `/retrieve`
- Full RAG question answering using `/query`
- Custom question testing outside the benchmark set
- Retrieved chunks and reranking scores
- Generated answers and source attribution
- Per-question latency
- Expected source retrieval status
- Expected source rank
- Top retrieved source
- Benchmark evaluation results

The dashboard is served from the `app/static` directory and is mounted by `app/main.py`.

---

# Bonus Challenge — Evaluation Dashboard

## Option D — Evaluation Dashboard

Bonus Challenge D has been implemented as an interactive evaluation dashboard.

The dashboard allows an evaluator to:

1. Run the benchmark evaluation.
2. View retrieval recall.
3. View average latency.
4. Inspect individual benchmark questions.
5. Inspect expected and retrieved sources.
6. View expected source ranking.
7. Test custom questions.
8. Test retrieval without using the LLM.
9. Test the complete RAG pipeline using the LLM.
10. Inspect retrieved chunks, scores, answers, and sources.

This allows retrieval quality and generation quality to be inspected independently.

---

## Evaluation Semantics

The benchmark currently evaluates retrieval using expected source-document recall.

A question is considered a retrieval `PASS` when the expected source document appears anywhere in the retrieved candidate set.

For example:

    Expected Source:
    02_nexus_api_reference.txt

    Retrieved Sources:
    1. 05_nexus_changelog.txt
    2. 02_nexus_api_reference.txt
    3. 04_nexus_troubleshooting_guide.txt

The result is:

    Status: PASS
    Expected Retrieved: YES
    Expected Rank: 2
    Top Source: 05_nexus_changelog.txt

Therefore, `PASS` does not necessarily mean that the expected source was ranked first.

The dashboard explicitly displays:

- `Status` — whether the expected source was retrieved
- `Expected Source` — the source expected by the benchmark
- `Expected Retrieved` — whether the expected source appears in the retrieved candidates
- `Expected Rank` — the 1-based position of the expected source
- `Top Source` — the highest-ranked retrieved document
- `Top Score` — score of the highest-ranked result
- `Latency` — query processing latency

This makes it possible to distinguish between:

    Expected Rank = 1

Strong top-ranked retrieval.

and:

    Expected Rank > 1

Expected source was retrieved but was not the highest-ranked result.

and:

    Expected Rank = Not Found

Retrieval failure.

---

# Custom Question Testing

The dashboard allows users to enter any question related to the Nexus documentation.

Example:

    What authentication methods does Nexus support?

The user can then choose between:

    [ Test Retrieval ]    [ Ask AI ]

---

## Test Retrieval

Clicking:

    Test Retrieval

calls:

    POST /retrieve

with:

    {
      "question": "What authentication methods does Nexus support?"
    }

This performs:

    Question
       |
       v
    BM25 Retrieval + Vector Retrieval
       |
       v
    Reciprocal Rank Fusion
       |
       v
    Reranking
       |
       v
    Relevant Chunks

The retrieval-only operation does **not** call the OpenAI API.

The dashboard displays:

- Question
- Retrieved documents
- Chunk IDs
- Reranking scores
- Retrieved chunk text
- Retrieval latency

This allows the retrieval pipeline to be tested independently from LLM generation.

---

## Ask AI

Clicking:

    Ask AI

calls:

    POST /query

with:

    {
      "question": "What authentication methods does Nexus support?"
    }

This performs the complete RAG pipeline:

    Question
       |
       v
    Hybrid Retrieval
       |
       v
    Reciprocal Rank Fusion
       |
       v
    Reranking
       |
       v
    Relevant Context
       |
       v
    OpenAI LLM
       |
       v
    Grounded Answer + Sources

The dashboard displays:

- Question
- Generated answer
- Source documents
- Source scores
- Available retrieved context
- Latency

A valid `OPENAI_API_KEY` is required because `/query` uses the OpenAI API for final answer generation.

---

## Difference Between `/retrieve` and `/query`

### `/retrieve`

    Question
       ↓
    BM25
       +
    Vector Search
       ↓
    RRF
       ↓
    Reranking
       ↓
    Retrieved Chunks

No OpenAI generation is performed.

Use `/retrieve` when you want to:

- Test retrieval
- Inspect retrieved documents
- Inspect reranking scores
- Debug retrieval
- Test the system without an LLM API call

### `/query`

    Question
       ↓
    BM25
       +
    Vector Search
       ↓
    RRF
       ↓
    Reranking
       ↓
    Retrieved Chunks
       ↓
    Grounded Prompt
       ↓
    OpenAI
       ↓
    Answer + Sources

Use `/query` when you want to:

- Test the complete RAG pipeline
- Generate a grounded answer
- Inspect source attribution
- Evaluate the final user-facing response

---

# `POST /retrieve`

The `/retrieve` endpoint allows the retrieval pipeline to be tested independently from LLM generation.

### Example Request

    POST /retrieve
    Content-Type: application/json

    {
      "question": "What authentication methods does Nexus support?"
    }

### Example Response

    {
      "chunks": [
        {
          "document": "07_nexus_security_compliance.txt",
          "chunk_id": "07_nexus_security_compliance.txt__1",
          "score": 0.5174,
          "text": "..."
        },
        {
          "document": "02_nexus_api_reference.txt",
          "chunk_id": "02_nexus_api_reference.txt__1",
          "score": 0.4166,
          "text": "..."
        }
      ],
      "latency_ms": 867
    }

The exact retrieved chunks, scores, and latency may vary between runs.

---

## Testing `/retrieve` Using Swagger

Open:

    http://localhost:8000/docs

Select:

    POST /retrieve

Click **Try it out**, then use:

    {
      "question": "What authentication methods does Nexus support?"
    }

Click **Execute** to inspect the retrieved and reranked chunks.

---

# `POST /query`

The `/query` endpoint runs the complete RAG pipeline.

### Example Request

    POST /query
    Content-Type: application/json

    {
      "question": "What authentication methods does Nexus support?"
    }

### Example Response

    {
      "answer": "Nexus supports OAuth 2.0 / OIDC for user authentication. It also offers support for SSO integrations with Okta, Azure AD, Google Workspace, and SAML 2.0 providers.",
      "sources": [
        {
          "document": "07_nexus_security_compliance.txt",
          "chunk_id": "07_nexus_security_compliance.txt__1",
          "score": 0.5174,
          "page": null
        },
        {
          "document": "02_nexus_api_reference.txt",
          "chunk_id": "02_nexus_api_reference.txt__1",
          "score": 0.4166,
          "page": null
        }
      ],
      "latency_ms": 624
    }

The exact latency and retrieved results may vary between runs.

---

## Testing `/query` Using Swagger

Open:

    http://localhost:8000/docs

Select:

    POST /query

Click **Try it out**, then use:

    {
      "question": "What authentication methods does Nexus support?"
    }

Click **Execute**.

A valid `OPENAI_API_KEY` is required because `/query` uses the OpenAI API for final answer generation.

---

# Evaluation

The benchmark questions are stored in:

    evaluation/questions.json

The evaluation logic is implemented in:

    evaluation/evaluate.py

Run the evaluation script from the repository root:

    python evaluation/evaluate.py

The script loads the benchmark questions, runs the retrieval pipeline, prints reranked chunks, generates answers, and reports recall and latency.

The evaluation reports:

- Retrieval success/failure
- Expected source documents
- Retrieved source documents
- Top reranked chunks
- Reranking scores
- Generated answers
- Per-question latency
- Overall retrieval recall
- Average latency

---

## Running Evaluation Through the Dashboard

The dashboard also provides a:

    Run Evaluation

button.

This calls:

    POST /evaluation/run

and displays the latest evaluation results.

The dashboard should be used when you want a visual representation of the benchmark.

The command-line evaluation can still be used when you want raw evaluation output in the terminal.

---

# Evaluation Results

A recent evaluation run on the five benchmark questions produced:

    ================================================
    RAG Evaluation
    ================================================

    Benchmark Questions: 5

    Retrieval Recall: 1.00
    Average Latency: 2178 ms

The reported latency includes model initialization/cold-start overhead in the current evaluation setup. Individual query latency can be significantly lower after the required models are loaded.

The five benchmark questions successfully retrieved their expected source document within the retrieved candidate set.

The 100% recall result should therefore be interpreted as benchmark source-document recall rather than a guarantee that the expected document was always ranked first.

---

## Example Evaluation

    Question:
    What authentication methods does Nexus support?

    Expected source:
    07_nexus_security_compliance.txt

    Retrieval:
    PASS

    Expected Rank:
    1

    Top reranked source:
    07_nexus_security_compliance.txt

    Generated answer:
    Nexus supports OAuth 2.0 / OIDC for user authentication.
    It also offers support for SSO integrations with Okta,
    Azure AD, Google Workspace, and SAML 2.0 providers.

---

# Retrieval Evaluation Interpretation

The current benchmark demonstrates:

    Benchmark Questions: 5
    Retrieval Recall: 100%
    Hybrid Retrieval: Enabled
    Reciprocal Rank Fusion: Enabled
    Reranking: Enabled
    LLM Generation: Enabled
    Interactive Evaluation Dashboard: Enabled
    Custom Question Testing: Enabled

The evaluation dataset contains only five benchmark questions, so the 100% recall result should be interpreted as performance on this benchmark rather than a general guarantee of retrieval accuracy.

The dashboard also exposes the expected source rank, which provides additional information about retrieval quality beyond simple source recall.

---

# Design Decisions

## Vector Database

ChromaDB was selected because the assignment dataset is relatively small and the primary goal is to demonstrate a complete RAG implementation without introducing unnecessary infrastructure complexity.

Advantages:

- Simple local setup
- Python integration
- Persistent local collections
- Suitable for development and evaluation

For a larger production deployment, a distributed vector database such as Qdrant, Pinecone, or PostgreSQL with pgvector could be considered.

---

## Embedding Model

SentenceTransformers is used to generate dense vector representations of document chunks.

Semantic embeddings allow the system to retrieve relevant information even when the query wording differs from the wording in the source document.

---

## Hybrid Retrieval

BM25 and vector retrieval are combined because they have complementary strengths.

BM25 is effective for exact technical terms, while vector search is better at semantic similarity.

The results are combined using Reciprocal Rank Fusion before reranking.

---

## Chunking Strategy

Documents are split into overlapping chunks so that retrieved passages contain enough context while remaining small enough for efficient retrieval and generation.

The exact chunk size and overlap configuration are documented in the design document.

---

# Grounding Strategy

The LLM receives the retrieved documentation as context.

The generation prompt instructs the model to:

1. Answer using the supplied documentation.
2. Avoid unsupported claims.
3. Avoid using outside knowledge.
4. State when the answer cannot be found in the provided documents.

This helps reduce hallucinations and keeps responses grounded in the Nexus documentation.

---

# Production Considerations

The assignment asks us to consider a deployment serving approximately 50,000 users per day.

A production architecture could use:

                         Users
                           |
                           v
                    Load Balancer
                           |
              +------------+------------+
              |            |            |
              v            v            v
          FastAPI #1   FastAPI #2   FastAPI #3
              |            |            |
              +------------+------------+
                           |
                           v
                    Retrieval Service
                           |
               +-----------+-----------+
               |                       |
               v                       v
          Vector Database          BM25 Index
               |                       |
               +-----------+-----------+
                           |
                           v
                       Reranker
                           |
                           v
                      LLM Provider
                           |
                           v
                        Response

## API Layer

Multiple FastAPI instances can run behind a load balancer.

This allows horizontal scaling as request volume increases.

## Vector Database

The local ChromaDB setup is suitable for development and evaluation.

For production, a managed or distributed vector store could be used depending on scale and operational requirements.

## LLM Layer

The LLM layer can use an external API or a self-hosted model depending on cost, latency, privacy, and operational requirements.

## Monitoring

Important metrics include:

- Request count
- API latency
- Retrieval latency
- LLM latency
- Error rate
- Retrieval quality
- Token usage
- Infrastructure cost
- Cache hit rate

## Logging

Production logs should include:

- Request ID
- Query metadata
- Retrieved document IDs
- Retrieval scores
- Latency
- Model information
- Errors

Sensitive user data should not be logged unnecessarily.

## Cost Optimization

Potential optimizations include:

- Response caching
- Retrieval caching
- Limiting context size
- Selecting models based on query complexity
- Avoiding unnecessary LLM calls
- Batching where appropriate

## Latency Optimization

Potential optimizations include:

- Reusing loaded embedding and reranking models
- Persistent vector indexes
- Retrieval caching
- Parallel BM25 and vector retrieval
- Limiting the number of chunks passed to the LLM
- Separating cold-start/model initialization latency from per-query latency

## Scaling Strategy

The API layer can be horizontally scaled using multiple stateless instances.

The retrieval and storage layers should use shared infrastructure so that API instances do not maintain independent copies of the production knowledge base.

---

# Limitations

- Answer generation requires a valid `OPENAI_API_KEY`.
- Evaluation currently uses a fixed benchmark set of five questions.
- Retrieval recall is evaluated using expected source documents rather than a large labeled relevance dataset.
- A retrieval `PASS` means the expected source was found in the retrieved candidate set; it does not necessarily mean it was ranked first.
- Response quality is currently assessed through manual observation rather than an automated LLM-as-a-judge metric.
- The current reranking implementation uses semantic similarity and score blending.
- Source attribution is based on chunk metadata and does not currently provide page numbers for plain-text documents.
- The API does not currently implement authentication.
- Production-grade API rate limiting is not implemented.
- The local ChromaDB configuration is intended for development/evaluation rather than high-scale production deployment.
- Current evaluation latency can include model initialization/cold-start overhead.

---

# Future Improvements

With additional development time, the system could be improved by adding:

- Larger and more diverse evaluation datasets
- Automated answer-quality evaluation
- Better reranking models
- Query expansion
- Retrieval caching
- Response caching
- API authentication
- API rate limiting
- Observability and tracing
- Docker-based deployment
- Distributed vector storage
- Production monitoring
- Horizontal API scaling

---

# Reflection

The most important engineering decision was choosing hybrid retrieval instead of relying only on semantic vector similarity. Technical documentation contains both natural-language concepts and exact identifiers, so BM25 and embeddings provide complementary retrieval signals.

The addition of the retrieval-only `/retrieve` endpoint makes it possible to inspect retrieval independently from LLM generation. This is useful for debugging retrieval quality and understanding whether an incorrect answer originates from retrieval or generation.

The evaluation dashboard further improves this workflow by providing a visual view of benchmark performance and allowing custom questions to be tested through both retrieval-only and full RAG paths.

With an additional week, I would focus on improving evaluation coverage, automated response-quality measurement, reranking quality, caching, and production observability.

I would also like to learn more about production-scale vector databases, retrieval evaluation, and LLM observability.

AI tools were used as engineering assistants during implementation for debugging, API design, code review, dependency troubleshooting, and exploring retrieval strategies. Generated code and suggestions were validated through local execution and the evaluation pipeline rather than being accepted without testing.

---

# Conclusion

This project demonstrates a complete document-grounded RAG pipeline using:

    Document Ingestion
            ↓
        Chunking
            ↓
     Embeddings + BM25
            ↓
     Hybrid Retrieval
            ↓
    Reciprocal Rank Fusion
            ↓
        Reranking
            ↓
     Grounded Context
            ↓
      LLM Generation
            ↓
      Answer + Sources

The system provides two primary API paths:

    POST /retrieve

for independently inspecting retrieval results, and:

    POST /query

for the complete retrieval + generation workflow.

It also provides:

    POST /evaluation/run

for running the benchmark evaluation and:

    GET /dashboard

for the interactive evaluation dashboard.

The dashboard allows users to:

- View benchmark metrics
- Inspect retrieval results
- Compare expected and top-ranked sources
- View expected source rank
- Run the benchmark
- Test custom questions using `/retrieve`
- Test custom questions using `/query`

On the provided five-question benchmark, the latest evaluation achieved:

    Retrieval Recall: 100%
    Average Latency: 2178 ms

The latency includes model initialization/cold-start overhead in the current evaluation setup.

The implementation demonstrates practical RAG engineering, hybrid retrieval, Reciprocal Rank Fusion, reranking, retrieval evaluation, API design, interactive evaluation, grounding, and production-oriented system thinking.