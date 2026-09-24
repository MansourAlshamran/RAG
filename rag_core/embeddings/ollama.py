from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document


def get_embedding_model():
    return OllamaEmbeddings(model="bge-m3")

def embed_chunks(chunk_list: list[Document]) -> list[list[float]]:
    msg = "Embedding text..."
    print(msg)

    embeddengs = get_embedding_model()
    text = [chunk.page_content for chunk in chunk_list]

    return embeddengs.embed_documents(text)

def embed_query(question: str) -> list[float]:
    embeddings = get_embedding_model()

    return embeddings.embed_query(question)