import os
from typing import Literal
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document

SUPPORTED_FORMATS = Literal['.txt', '.pdf', '.docx']

class UnsupportedFileTypeError(Exception):
    pass

def extract_text(file_path: str) -> str:
    """
    Extracts text from .txt, .pdf, and .docx files.

    :param file_path: Absolute path to the input file.
    :return: Extracted text as a string.
    :raises FileNotFoundError: If the file doesn't exist.
    :raises UnsupportedFileTypeError: If the file format is not supported.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ File not found: {file_path}")

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == '.txt':
        return _extract_txt(file_path)
    elif ext == '.pdf':
        return _extract_pdf(file_path)
    elif ext == '.docx':
        return _extract_docx(file_path)
    else:
        raise UnsupportedFileTypeError(
            f"❌ Unsupported file format: '{ext}'. Supported formats: .txt, .pdf, .docx"
        )

def _extract_txt(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def _extract_pdf(file_path: str) -> str:
    try:
        return extract_pdf_text(file_path)
    except Exception as e:
        raise RuntimeError(f"❌ Failed to extract text from PDF: {e}")

def _extract_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
    except Exception as e:
        raise RuntimeError(f"❌ Failed to extract text from DOCX: {e}")
