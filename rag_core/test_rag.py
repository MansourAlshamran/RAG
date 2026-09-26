from rag_core.ingestion.pipeline import docs_pipeline
from rag_core.rag import chat

if __name__ == "__main__":

    docs_pipeline(
        file="Mansour_CV_Software_AI_Engineer.pdf",
        domain="CV"
    )

    response = chat("What experience does Mansour have?")

    print(response)