from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str

class SaveDocumentRequest(BaseModel):
    filename: str
    domain: str