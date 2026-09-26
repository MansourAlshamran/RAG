from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from rag_core.rag import chat
from app.schemas import ChatRequest, SaveDocumentRequest
from rag_core.ingestion.pipeline import docs_pipeline


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = Path(__file__).resolve().parents[1] / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/documents/upload")
async def upload_endpoint(file: UploadFile = File(...)):
    filename = Path(file.filename).name
    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return {
        "success": True,
        "filename": filename,
        "message": "File uploaded successfully."
    }


@app.post("/documents/save")
def save_document_endpoint(document: SaveDocumentRequest):
    result = docs_pipeline(document.filename, document.domain)

    return result


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    return chat(request.message)
