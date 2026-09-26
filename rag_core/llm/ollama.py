from langchain_ollama import ChatOllama

def get_llm():

    return ChatOllama(
        model="llama3.2:3b",
        temperature=0
    )

def generate_response(prompt: str) -> str:
    llm = get_llm()
    response = llm.invoke(prompt)

    return response.content
