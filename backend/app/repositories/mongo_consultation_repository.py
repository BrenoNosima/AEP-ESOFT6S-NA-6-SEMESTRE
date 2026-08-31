from __future__ import annotations

from pymongo.database import Database

from app.domain.interfaces.consultation_repository import ConsultationRepository
from app.domain.models.consultation import Consultation


class MongoConsultationRepository(ConsultationRepository):
    """Implementação de ConsultationRepository sobre a coleção única `consultations`."""

    _COLLECTION_NAME = "consultations"

    def __init__(self, database: Database) -> None:
        self._collection = database[self._COLLECTION_NAME]

    def save(self, consultation: Consultation) -> Consultation:
        self._collection.insert_one(self._to_document(consultation))
        return consultation

    def list_all(self) -> list[Consultation]:
        documents = self._collection.find().sort("created_at", -1)
        return [self._to_entity(document) for document in documents]

    def get_by_id(self, consultation_id: str) -> Consultation | None:
        document = self._collection.find_one({"_id": consultation_id})
        return self._to_entity(document) if document else None

    def delete(self, consultation_id: str) -> bool:
        result = self._collection.delete_one({"_id": consultation_id})
        return result.deleted_count > 0

    @staticmethod
    def _to_document(consultation: Consultation) -> dict:
        return {
            "_id": consultation.id,
            "question": consultation.question,
            "category": consultation.category,
            "answer": consultation.answer,
            "created_at": consultation.created_at,
        }

    @staticmethod
    def _to_entity(document: dict) -> Consultation:
        return Consultation(
            id=document["_id"],
            question=document["question"],
            category=document["category"],
            answer=document["answer"],
            created_at=document["created_at"],
        )
