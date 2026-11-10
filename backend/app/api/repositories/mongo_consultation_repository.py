from __future__ import annotations

from dataclasses import asdict

from pymongo import ReturnDocument
from pymongo.database import Database

from app.api.repositories._mongo_errors import translate_errors
from app.domain.interfaces.consultation_repository import ConsultationRepository
from app.domain.models.consultation import Consultation
from app.domain.models.location import Location


class MongoConsultationRepository(ConsultationRepository):
    """Implementação de ConsultationRepository sobre a coleção `consultations`.

    `user_id` referencia `users._id` (relacionamento por referência) e `location`
    é um subdocumento `{city, state}`.
    """

    _COLLECTION_NAME = "consultations"

    def __init__(self, database: Database) -> None:
        self._collection = database[self._COLLECTION_NAME]
        self._collection.create_index([("created_at", -1)])
        self._collection.create_index([("category", 1), ("created_at", -1)])
        self._collection.create_index([("user_id", 1), ("created_at", -1)])

    @translate_errors
    def save(self, consultation: Consultation) -> Consultation:
        self._collection.insert_one(self._to_document(consultation))
        return consultation

    @translate_errors
    def list_all(
        self,
        *,
        category: str | None = None,
        user_id: str | None = None,
        limit: int = 50,
        skip: int = 0,
    ) -> list[Consultation]:
        query = {}
        if category:
            query["category"] = category
        if user_id:
            query["user_id"] = user_id
        documents = (
            self._collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        )
        return [self._to_entity(document) for document in documents]

    @translate_errors
    def get_by_id(self, consultation_id: str) -> Consultation | None:
        document = self._collection.find_one({"_id": consultation_id})
        return self._to_entity(document) if document else None

    @translate_errors
    def delete(self, consultation_id: str) -> bool:
        result = self._collection.delete_one({"_id": consultation_id})
        return result.deleted_count > 0

    @translate_errors
    def delete_by_user(self, user_id: str) -> int:
        return self._collection.delete_many({"user_id": user_id}).deleted_count

    @translate_errors
    def count_by_category(self, user_id: str) -> dict[str, int]:
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$category", "total": {"$sum": 1}}},
            {"$sort": {"total": -1, "_id": 1}},
        ]
        return {row["_id"]: row["total"] for row in self._collection.aggregate(pipeline)}

    @translate_errors
    def update_category(self, consultation_id: str, category: str) -> Consultation | None:
        document = self._collection.find_one_and_update(
            {"_id": consultation_id},
            {"$set": {"category": category}},
            return_document=ReturnDocument.AFTER,
        )
        return self._to_entity(document) if document else None

    @staticmethod
    def _to_document(consultation: Consultation) -> dict:
        return {
            "_id": consultation.id,
            "question": consultation.question,
            "category": consultation.category,
            "answer": consultation.answer,
            "created_at": consultation.created_at,
            "user_id": consultation.user_id,
            "location": asdict(consultation.location) if consultation.location else None,
        }

    @staticmethod
    def _to_entity(document: dict) -> Consultation:
        # .get(): documentos da 1ª entrega não têm user_id nem location.
        location = document.get("location")
        return Consultation(
            id=document["_id"],
            question=document["question"],
            category=document["category"],
            answer=document["answer"],
            created_at=document["created_at"],
            user_id=document.get("user_id"),
            location=Location(city=location["city"], state=location["state"])
            if location
            else None,
        )
