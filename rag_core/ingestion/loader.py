from langchain_core.documents import Document
from pathlib import Path
import re
from pypdf import PdfReader


def clean_text(text: str) -> str:
    """Normalize common PDF extraction artifacts without removing meaning."""
    
    text = text.translate(str.maketrans({"\u00a0": " ", "\u2022": "-", "\u2013": "-", "\u2014": "-"}))
    text = text.replace("\ufffd", "")

    lines = (re.sub(r"\s+", " ", line).strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)


def load_pdf(domain, file_path: str | Path) -> list[Document]:
    msg = "Cleaning extracted text..."
    print(msg)

    reader = PdfReader(file_path)

    return [
        Document(
            page_content=clean_text(page.extract_text() or ""),
            metadata={"domain": domain, "source": str(file_path), "page": i + 1},
        )
        for i, page in enumerate(reader.pages)
    ]


