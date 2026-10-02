from fastapi import APIRouter, HTTPException

from backend.ai_core.gemini_generator import (
    GeminiConfigurationError,
    GeminiDocumentGenerator,
    GeminiGenerationError,
    LEGAL_DISCLAIMER,
)

from backend.config import get_settings

from backend.schemas import (
    DocumentRequest,
    DocumentResponse,
)


router = APIRouter()


@router.post(
    "/generate",
    response_model=DocumentResponse,
)
def generate_document(
    request: DocumentRequest,
):

    try:

        settings = get_settings()

        generator = GeminiDocumentGenerator(
            settings
        )

        content = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates,
            jurisdiction=request.jurisdiction,
        )

        return DocumentResponse(
            document_type=request.document_type,
            content=content,
            model=settings.gemini_model,
            disclaimer=LEGAL_DISCLAIMER,
        )

    except GeminiConfigurationError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except GeminiGenerationError as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc