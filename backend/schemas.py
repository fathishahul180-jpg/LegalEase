from pydantic import BaseModel, Field
from typing import Any


class DocumentRequest(BaseModel):
    document_type: str
    parties: Any = Field(default_factory=dict)
    terms: Any = Field(default_factory=list)
    dates: Any = Field(default_factory=dict)
    jurisdiction: str = ""


class DocumentResponse(BaseModel):
    document_type: str
    content: str
    model: str
    disclaimer: str