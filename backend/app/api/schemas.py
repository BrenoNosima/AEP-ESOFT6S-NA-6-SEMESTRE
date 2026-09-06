from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.domain.models.consultation import Consultation


class ConsultationCategory(str, Enum):
    residuos = "residuos"
    agua = "agua"
    energia = "energia"
    consumo = "consumo"
    geral = "geral"


Question = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=5, max_length=500)
]


class ConsultationRequest(BaseModel):
    question: Question = Field(examples=["Posso jogar óleo de cozinha na pia?"])
    category: ConsultationCategory = Field(examples=[ConsultationCategory.residuos])


class ConsultationCategoryUpdate(BaseModel):
    category: ConsultationCategory = Field(examples=[ConsultationCategory.agua])


class ConsultationResponse(BaseModel):
    id: str
    question: str
    category: str
    answer: str
    created_at: datetime

    @classmethod
    def from_domain(cls, consultation: Consultation) -> "ConsultationResponse":
        return cls(
            id=consultation.id,
            question=consultation.question,
            category=consultation.category,
            answer=consultation.answer,
            created_at=consultation.created_at,
        )
