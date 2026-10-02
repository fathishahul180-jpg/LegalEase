
from google import genai
from backend.config import get_settings

LEGAL_DISCLAIMER = (
    "This document is an AI-generated draft. "
    "Consult a qualified legal professional before signing."
)


class GeminiConfigurationError(Exception):
    pass


class GeminiGenerationError(Exception):
    pass


class GeminiDocumentGenerator:
    def __init__(self, settings=None):
        self.settings = settings or get_settings()

        if not self.settings.gemini_api_key:
            raise GeminiConfigurationError(
                "Gemini API key is missing. Set it in .env."
            )

        self.client = genai.Client(
            api_key=self.settings.gemini_api_key
        )

    def generate_document(
        self,
        document_type,
        parties,
        terms,
        dates,
        jurisdiction,
    ):
        prompt = f"""
        Draft a professional legal document using only
        the following information.

        Document type: {document_type}
        Parties: {parties}
        Terms: {terms}
        Dates: {dates}
        Jurisdiction: {jurisdiction or "Not provided"}

        Do not invent legal citations, facts, names, or dates.
        Use placeholders for missing information.
        Include a Review Before Signing section.
        """

        try:
            response = self.client.models.generate_content(
                model=self.settings.gemini_model,
                contents=prompt,
            )

            if not response.text:
                raise GeminiGenerationError(
                    "Gemini returned an empty response."
                )

            return response.text

        except GeminiGenerationError:
            raise
        except Exception as exc:
            raise GeminiGenerationError(str(exc)) from exc