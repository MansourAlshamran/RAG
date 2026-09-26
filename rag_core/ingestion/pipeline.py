from pathlib import Path

from rag_core.ingestion.loader import load_pdf
from rag_core.ingestion.splitter import split_documents
from rag_core.embeddings.ollama import embed_chunks
from rag_core.vectorstore.chroma import store_data

def docs_pipeline(file, domain):
    pdf_path = Path(__file__).resolve().parents[2] / "data" / "uploads" / file

    doc = load_pdf(domain, pdf_path)
    chunks = split_documents(doc)
    embeddings = embed_chunks(chunks)

    result = store_data(
        ids_list = [chunk.metadata["id"] for chunk in chunks],
        embeddings_list = embeddings,
        metadatas_list = [chunk.metadata for chunk in chunks],
        chunks_list = [chunk.page_content for chunk in chunks],
    )
    

    if result["success"]:
        print(f"\n[✓] {result['message']}")
        print(f"    Stored chunks: {result['stored_count']}\n")
    else:
        print(f"\n[✗] {result['message']}\n")

    return result
