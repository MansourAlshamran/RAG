from rag_core.retrieval.retriever import retriever
from rag_core.llm.ollama import generate_response

def chat(question):
    results = retriever(question)
    context = "\n\n".join(results["documents"][0])

    prompt = f"""
    Answer the question using only the provided context

    context:
    {context}

    question:
    {question}
    """

    return generate_response(prompt)