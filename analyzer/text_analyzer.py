from typing import List, Dict, Any
import spacy
import pytextrank

# Load spaCy English model with PyTextRank pipeline for keyword extraction
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("textrank")

class TextAnalyzer:


    def __init__(self):
        self.nlp = nlp

    def analyze(self, text: str) -> Dict[str, Any]:

        if not text or not text.strip():
            raise ValueError("Input text is empty or None.")

        doc = self.nlp(text)

        return {
            "summary": self._generate_summary(doc),
            "key_phrases": self._extract_key_phrases(doc),
            "named_entities": self._extract_named_entities(doc)
        }

    def _generate_summary(self, doc) -> str:

        # Select top-ranked sentences (max 3 sentences)
        top_sentences = sorted(doc._.textrank.summary(limit_phrases=15, limit_sentences=3),
                               key=lambda sent: sent.start)
        summary = " ".join([sent.text for sent in top_sentences])
        return summary

    def _extract_key_phrases(self, doc) -> List[str]:

        phrases = [phrase.text for phrase in doc._.phrases[:10]]  # top 10 phrases
        return phrases

    def _extract_named_entities(self, doc) -> List[Dict[str, str]]:

        entities = []
        for ent in doc.ents:
            entities.append({"text": ent.text, "label": ent.label_})
        return entities
