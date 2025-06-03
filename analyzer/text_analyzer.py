from typing import List, Dict, Any, Optional
import spacy
import pytextrank
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TextAnalyzer:
    """
    TextAnalyzer performs text summarization, key phrase extraction,
    and named entity recognition using spaCy and pytextrank.
    """

    def __init__(
        self,
        model_name: str = "en_core_web_sm",
        summary_sentences: int = 3,
        key_phrases_count: int = 10,
    ):
        """
        Initialize the TextAnalyzer.

        Args:
            model_name (str): spaCy model to load.
            summary_sentences (int): Number of sentences in summary.
            key_phrases_count (int): Number of key phrases to extract.
        """
        try:
            self.nlp = spacy.load(model_name)
            # Check if pytextrank is already added; if not, add it
            if "textrank" not in self.nlp.pipe_names:
                self.nlp.add_pipe("textrank")
        except Exception as e:
            logger.error(f"Failed to load spaCy model or add pytextrank: {e}")
            raise RuntimeError(f"Initialization error: {e}")

        self.summary_sentences = summary_sentences
        self.key_phrases_count = key_phrases_count

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text to extract summary, key phrases, and named entities.

        Args:
            text (str): Input text to analyze.

        Returns:
            dict: Analysis results with keys 'summary', 'key_phrases', 'named_entities'.
        """
        if not text or not text.strip():
            raise ValueError("Input text is empty or None.")

        try:
            doc = self.nlp(text)
        except Exception as e:
            logger.error(f"Error during NLP processing: {e}")
            raise RuntimeError(f"Processing error: {e}")

        try:
            summary = self._generate_summary(doc)
        except Exception as e:
            logger.warning(f"Summary generation failed: {e}")
            summary = ""

        try:
            key_phrases = self._extract_key_phrases(doc)
        except Exception as e:
            logger.warning(f"Key phrase extraction failed: {e}")
            key_phrases = []

        try:
            named_entities = self._extract_named_entities(doc)
        except Exception as e:
            logger.warning(f"Named entity extraction failed: {e}")
            named_entities = []

        return {
            "summary": summary,
            "key_phrases": key_phrases,
            "named_entities": named_entities,
        }

    def _generate_summary(self, doc) -> str:
        # Get top sentences by textrank, sorted by order of appearance
        top_sentences = sorted(
            doc._.textrank.summary(
                limit_phrases=self.key_phrases_count,
                limit_sentences=self.summary_sentences,
            ),
            key=lambda sent: sent.start,
        )
        summary = " ".join([sent.text for sent in top_sentences])
        return summary

    def _extract_key_phrases(self, doc) -> List[str]:
        # Extract top key phrases
        phrases = [phrase.text for phrase in doc._.phrases[: self.key_phrases_count]]
        return phrases

    def _extract_named_entities(self, doc) -> List[Dict[str, str]]:
        # Extract named entities with their labels
        entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
        return entities
