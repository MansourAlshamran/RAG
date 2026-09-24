import chromadb

from rag_core.embeddings.ollama import embed_query

def retriever(question):
    query_embedding = embed_query(question)