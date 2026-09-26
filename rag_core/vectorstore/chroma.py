from pathlib import Path
import chromadb


DB_PATH = Path(__file__).resolve().parents[2] / "data" / "chroma"

def get_collection():
    client = chromadb.PersistentClient(path=str(DB_PATH))
    return client.get_or_create_collection(name="knowledge_base")

def store_data(ids_list: list, embeddings_list: list, metadatas_list: list, chunks_list: list):
    msg = "Saving data to vectoreDB..."

    lenghts = {
        "ids": len(ids_list),
        "embeddings": len(embeddings_list),
        "metadatas": len(metadatas_list),
        "chunks": len(chunks_list)
    }

    if len(set(lenghts.values())) != 1:
        return {
            "success": False,
            "stored_count": 0,
            "message": f"Data mismatch; nothing was saved. Details: {lenghts}",
        }
    
    if not ids_list:
        return {
            "success": False,
            "stored_count": 0,
            "message": "No readable text chunks were found in the uploaded file."
        }

    print(msg)

    collection = get_collection()

    collection.upsert(
        ids = ids_list,
        embeddings = embeddings_list,
        metadatas = metadatas_list,
        documents = chunks_list,
    )

    return {
        "success": True,
        "stored_count": len(ids_list),
        "message": "File saved successfully."
    }

def query_collection(query_embedding, n_results=5):
    collection = get_collection()

    return collection.query(
        query_embeddings = [query_embedding],
        n_results = n_results
    )
