from typing import List, Dict, Any
import spacy
import pytextrank

# Load spaCy English model with PyTextRank pipeline for keyword extraction
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("textrank")

class TextAnalyzer:
    """
    TextAnalyzer uses spaCy and PyTextRank to analyze text:
    - Summarize
    - Extract key phrases
    - Extract named entities
    """

    def __init__(self):
        self.nlp = nlp

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze the input text and extract insights.

        :param text: The raw text to analyze.
        :return: Dictionary containing summary, key_phrases, and named_entities.
        """
        if not text or not text.strip():
            raise ValueError("Input text is empty or None.")

        doc = self.nlp(text)

        return {
            "summary": self._generate_summary(doc),
            "key_phrases": self._extract_key_phrases(doc),
            "named_entities": self._extract_named_entities(doc)
        }

    def _generate_summary(self, doc) -> str:
        """
        Generate a summary by extracting top ranked sentences.

        :param doc: spaCy Doc object with PyTextRank pipeline.
        :return: Summary string.
        """
        # Select top-ranked sentences (max 3 sentences)
        top_sentences = sorted(doc._.textrank.summary(limit_phrases=15, limit_sentences=3),
                               key=lambda sent: sent.start)
        summary = " ".join([sent.text for sent in top_sentences])
        return summary

    def _extract_key_phrases(self, doc) -> List[str]:
        """
        Extract key phrases using PyTextRank.

        :param doc: spaCy Doc object.
        :return: List of key phrases.
        """
        phrases = [phrase.text for phrase in doc._.phrases[:10]]  # top 10 phrases
        return phrases

    def _extract_named_entities(self, doc) -> List[Dict[str, str]]:
        """
        Extract named entities like PERSON, ORG, GPE etc.

        :param doc: spaCy Doc object.
        :return: List of entities as dicts: {'text': str, 'label': str}
        """
        entities = []
        for ent in doc.ents:
            entities.append({"text": ent.text, "label": ent.label_})
        return entities
