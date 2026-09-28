# Modular Local RAG Template

A practical, local-first Retrieval-Augmented Generation (RAG) template for adding document question-answering to another Python application. It ingests PDF files, cleans and chunks their text, creates embeddings with Ollama, stores the result in ChromaDB, retrieves relevant chunks for a question, and asks a local LLM to answer from that context.

The project is deliberately organized as reusable modules rather than a one-off chatbot. You can use the included FastAPI service, or import the ingestion and chat functions directly from an existing backend, CLI, worker, or web application.

## What is implemented

- PDF ingestion with `pypdf`
- PDF-text cleanup and whitespace normalization
- Configurable recursive text chunking (currently 1,000 characters with 200-character overlap)
- Deterministic chunk IDs and document metadata (`domain`, source file, page, and chunk position)
- Local embeddings using Ollama's `bge-m3` model
- Persistent local ChromaDB vector storage
- Similarity retrieval for incoming questions
- Local answer generation using Ollama's `llama3.2:3b` model
- FastAPI endpoints for upload, ingestion, and chat

## Architecture

```text
    PDF upload
        |
        v
data/uploads/<file>.pdf
        |
        v
      load -> clean -> split -> generate IDs -> embed -> ChromaDB
                                                            |
                                                            v
                                                       data/chroma/
```
```text
Question -> query embedding -> Chroma similarity search -> retrieved text
                                                                   |
                                                                   v
                                                           Ollama chat model
                                                                   |
                                                                   v
                                                                 Answer
```

The core flow is implemented in `rag_core`:

| Module | Responsibility |
| --- | --- |
| `ingestion/loader.py` | Extracts and cleans text from a PDF, preserving source, page, and domain metadata. |
| `ingestion/splitter.py` | Splits LangChain documents into overlapping chunks and assigns chunk IDs. |
| `embeddings/ollama.py` | Creates document and query embeddings with Ollama. |
| `vectorstore/chroma.py` | Persists chunks, metadata, and vectors; performs similarity queries. |
| `retrieval/retriever.py` | Embeds a question and retrieves relevant Chroma records. |
| `rag.py` | Builds the context-grounded prompt and asks the chat model for an answer. |
| `ingestion/pipeline.py` | Orchestrates the full document-ingestion workflow. |
| `app/api.py` | Exposes the workflow through FastAPI. |

## Why this is a template

The application layer is intentionally thin. The RAG pipeline can be integrated into another system without coupling it to this FastAPI service or the starter frontend.

For example, an existing product can:

- Call `docs_pipeline(filename, domain)` after its own upload process.
- Call `chat(question)` from its own endpoint, job, or UI.
- Replace the Ollama embedding or chat adapters with hosted providers.
- Replace ChromaDB with another vector database behind the vector-store module.
- Add tenant, user, document type, or permission information to chunk metadata.

The current `domain` metadata field is ready for categories such as `medical`, `legal`, or even `cooking`. It is stored with every chunk. Domain-filtered retrieval is a natural next integration step; the current retriever searches the full knowledge base.

## Prerequisites

- Python 3.11 or newer
- [Ollama](https://ollama.com/) running locally
- The following Ollama models:
  - `bge-m3` for embeddings
  - `llama3.2:3b` for answer generation
- Node.js 20+ only if you plan to work on the optional React frontend

Pull the required local models:

```powershell
ollama pull bge-m3
ollama pull llama3.2:3b
```

If Ollama is not already running as a desktop/background service, start it in a separate terminal:

```powershell
ollama serve
```

## Quick start

From the repository root, create and activate a virtual environment.

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the API:

```powershell
python -m uvicorn app.api:app --reload
```

Open the interactive API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Try the current workflow

1. Upload a text-based PDF through `POST /documents/upload`.
2. Send its saved filename and a domain through `POST /documents/save`.
3. Ask a question through `POST /chat`.

PowerShell example:

```powershell
# 1. Upload a PDF. The API saves it under data/uploads/.
curl.exe -X POST "http://127.0.0.1:8000/documents/upload" `
  -F "file=@C:\path\to\clinical-guide.pdf"

# 2. Extract, clean, chunk, embed, and store it.
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/documents/save" `
  -ContentType "application/json" `
  -Body '{"filename":"clinical-guide.pdf","domain":"medical"}'

# 3. Ask the knowledge base a question.
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/chat" `
  -ContentType "application/json" `
  -Body '{"message":"What does the guide say about the recommended treatment?"}'
```

The save request uses Chroma's `upsert`, so rerunning an ingestion for the same chunk IDs updates existing records rather than failing on duplicate IDs.

## API reference

| Endpoint | Request | Purpose |
| --- | --- | --- |
| `POST /documents/upload` | `multipart/form-data` with a `file` field | Saves an uploaded file to `data/uploads/`. |
| `POST /documents/save` | `{ "filename": "file.pdf", "domain": "medical" }` | Runs the ingestion pipeline and stores the resulting chunks and vectors. |
| `POST /chat` | `{ "message": "Your question" }` | Retrieves relevant chunks and returns a model-generated answer. |

At present, the ingestion path is designed for PDFs with extractable text. A scanned/image-only PDF needs OCR before it can be used effectively.

## Programmatic integration

When another Python project already handles uploads and authentication, use the core functions directly:

```python
from rag_core.ingestion.pipeline import docs_pipeline
from rag_core.rag import chat

# The file must first exist in this project's data/uploads/ directory.
result = docs_pipeline(
    file="clinical-guide.pdf",
    domain="medical",
)

if result["success"]:
    answer = chat("What are the main recommendations?")
    print(answer)
else:
    print(result["message"])
```

For a more independent integration, adapt `docs_pipeline` to accept an absolute `Path` or upload stream rather than a filename. The existing functions already separate loading, splitting, embedding, storage, retrieval, and generation, so each stage can be replaced or called independently.

## Storage and metadata

Runtime data is intentionally local and ignored by Git:

```text
data/uploads/   # Original uploaded documents
data/chroma/    # ChromaDB's persistent local files
```

Each stored chunk includes text, its embedding vector, and metadata similar to:

```json
{
  "id": "...",
  "domain": "medical",
  "source": ".../data/uploads/clinical-guide.pdf",
  "page": 2,
  "start_index": 1200
}
```

Keep all text, metadata, and vectors in the same order when calling the vector-store adapter: element `0` in every list must describe the same chunk. The storage function validates list lengths before writing, preventing mismatched records from being saved.

## Configuration and model adapters

The active local models are defined in:

```python
# rag_core/embeddings/ollama.py
OllamaEmbeddings(model="bge-m3")

# rag_core/llm/ollama.py
ChatOllama(model="llama3.2:3b", temperature=0)
```

Change these values to use a different locally available Ollama model. Placeholder modules for alternative embedding and LLM providers are included under `rag_core/embeddings/` and `rag_core/llm/`, ready to be implemented when needed.

## Current scope and production considerations

This repository is a development template, not a production-hardened service. Before deploying it, consider adding:

- Authentication, authorization, and tenant isolation
- File type, file size, and malware validation before saving uploads
- OCR support for scanned PDFs
- Asynchronous/background ingestion for large files
- Better document IDs based on file-content hashes
- Metadata filters, especially domain and tenant filters, during retrieval
- Source citations in chat responses
- Structured logging, monitoring, retries, and error handling
- API rate limiting and CORS configuration appropriate for your deployment
- A real frontend; the included React/Vite app is currently a starter shell

## Development notes

Run the backend from the repository root so Python can resolve the `rag_core` package:

```powershell
python -m uvicorn app.api:app --reload
```

The project stores embeddings locally through ChromaDB and calls Ollama locally by default. This keeps document content on the machine running the service, subject to the behavior of any additional integrations you introduce.

## TODO

- [ ] Support additional document types: plain text (`.txt`), Markdown (`.md`), and images or scanned documents through OCR.
- [ ] Add a lightweight React user interface for uploading documents, selecting a domain, tracking ingestion, and chatting with the knowledge base. Keep the UI optional so the RAG core remains easy to integrate elsewhere.
- [ ] Add interchangeable chat and embedding providers, beginning with OpenAI and Google Gemini alongside Ollama.
- [ ] Strengthen error handling with clear API responses, validation, structured logs, retries where appropriate, and user-friendly recovery guidance.
