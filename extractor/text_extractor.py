import os
import sys
import spacy
from typing import List, Dict, Any
from collections import defaultdict
import re


class TextAnalyzer:
    def __init__(self):
        """Initialize the text analyzer with spaCy model"""
        try:
            # Try to load the model normally first
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            try:
                # Fallback for PyInstaller bundled executable
                import en_core_web_sm
                self.nlp = en_core_web_sm.load()
            except ImportError:
                # Final fallback - download the model if missing
                from spacy.cli import download
                download('en_core_web_sm')
                self.nlp = spacy.load('en_core_web_sm')

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text and return summary, key phrases, and named entities

        Args:
            text: Input text to analyze

        Returns:
            Dictionary containing:
            - summary: Generated summary
            - key_phrases: List of important phrases
            - named_entities: List of entities with types
        """
        if not text.strip():
            return {
                'summary': 'No text to analyze',
                'key_phrases': [],
                'named_entities': []
            }

        doc = self.nlp(text)

        # Extract key phrases (noun chunks)
        key_phrases = list(set(chunk.text.strip() for chunk in doc.noun_chunks if len(chunk.text.split()) > 1))

        # Extract named entities
        named_entities = [
            {'text': ent.text, 'label': ent.label_}
            for ent in doc.ents
        ]

        # Generate simple summary (first few sentences)
        sentences = [sent.text.strip() for sent in doc.sents]
        summary = ' '.join(sentences[:3]) + ('...' if len(sentences) > 3 else '')

        return {
            'summary': summary,
            'key_phrases': key_phrases,
            'named_entities': named_entities
        }


def extract_text(file_path: str) -> str:
    """
    Extracts text from .txt, .pdf, and .docx files.

    Args:
        file_path: Absolute path to the input file.

    Returns:
        Extracted text as a string.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        UnsupportedFileTypeError: If the file format is not supported.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

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
            f"Unsupported file format: '{ext}'. Supported formats: .txt, .pdf, .docx"
        )


def _extract_txt(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def _extract_pdf(file_path: str) -> str:
    try:
        from pdfminer.high_level import extract_text as extract_pdf_text
        return extract_pdf_text(file_path)
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")


def _extract_docx(file_path: str) -> str:
    try:
        from docx import Document
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from DOCX: {e}")