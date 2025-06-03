import os
from typing import Optional
from PyPDF2 import PdfReader
from docx import Document


def extract_text(file_path: str) -> Optional[str]:
    """Extract text from supported document types."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_pdf(file_path)
    elif ext == ".docx":
        return extract_docx(file_path)
    elif ext == ".txt":
        return extract_txt(file_path)
    else:
        raise ValueError("Unsupported file format. Supported formats: .pdf, .docx, .txt")


def extract_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join([page.extract_text() or "" for page in reader.pages])


def extract_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_txt(file_path: str) -> str:
    with open(file_path, encoding='utf-8') as f:
        return f.read()
