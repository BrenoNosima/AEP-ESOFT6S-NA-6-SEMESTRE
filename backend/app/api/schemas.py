from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.domain.models.category import Category as ConsultationCategory
from app.domain.models.consultation import Consultation
from app.domain.models.user import Address, User


Question = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=5, max_length=500)
]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)]
# Validação simples de formato, sem depender do pacote email-validator.
Email = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, to_lower=True, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    ),
]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
# O pattern é checado antes do to_upper, por isso aceita minúsculas ("pr" vira "PR").
State = Annotated[
    str, StringConstraints(strip_whitespace=True, to_upper=True, pattern=r"^[A-Za-z]{2}$")
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


class AddressSchema(BaseModel):
    street: Text = Field(examples=["Rua das Flores, 100"])
    city: Text = Field(examples=["Maringá"])
    state: State = Field(description="UF com 2 letras.", examples=["PR"])

    def to_domain(self) -> Address:
        return Address(street=self.street, city=self.city, state=self.state)

    @classmethod
    def from_domain(cls, address: Address) -> "AddressSchema":
        return cls(street=address.street, city=address.city, state=address.state)


class UserCreate(BaseModel):
    name: Name = Field(examples=["Ana Souza"])
    email: Email = Field(examples=["ana@example.com"])
    addresses: list[AddressSchema] = Field(
        default_factory=list,
        description="O primeiro endereço é usado para contextualizar as orientações.",
    )


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    addresses: list[AddressSchema]
    created_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            addresses=[AddressSchema.from_domain(a) for a in user.addresses],
            created_at=user.created_at,
        )


class CategoryTotal(BaseModel):
    category: str
    total: int


class UserConsultationsSummary(BaseModel):
    user_id: str
    total: int
    by_category: list[CategoryTotal]

    @classmethod
    def from_counts(cls, user_id: str, counts: dict[str, int]) -> "UserConsultationsSummary":
        return cls(
            user_id=user_id,
            total=sum(counts.values()),
            by_category=[CategoryTotal(category=c, total=t) for c, t in counts.items()],
        )
