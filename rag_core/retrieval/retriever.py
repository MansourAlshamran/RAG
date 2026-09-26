from rag_core.embeddings.ollama import embed_query
from rag_core.vectorstore.chroma import query_collection


def retriever(question: str, n_results=5):
    query_embedding = embed_query(question)

    return query_collection(
        query_embedding,
        n_results=n_results
    )
