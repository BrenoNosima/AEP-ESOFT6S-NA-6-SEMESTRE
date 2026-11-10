from __future__ import annotations

from dataclasses import asdict

from pymongo import ReturnDocument
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from app.api.repositories._mongo_errors import translate_errors
from app.domain.exceptions import ConflictError
from app.domain.interfaces.user_repository import UserRepository
from app.domain.models.user import Address, User


class MongoUserRepository(UserRepository):
    """Implementação de UserRepository sobre a coleção `users`.

    Os endereços ficam embutidos no documento do usuário como lista de
    subdocumentos (`addresses`), pois são poucos e sempre lidos junto com ele.
    """

    _COLLECTION_NAME = "users"

    def __init__(self, database: Database) -> None:
        self._collection = database[self._COLLECTION_NAME]
        self._collection.create_index("email", unique=True)
        self._collection.create_index([("created_at", -1)])

    @translate_errors
    def save(self, user: User) -> User:
        # DuplicateKeyError é um PyMongoError: tratado aqui, antes do decorator,
        # para virar erro de regra de negócio (409) e não falha de banco (503).
        try:
            self._collection.insert_one(self._to_document(user))
        except DuplicateKeyError as error:
            raise ConflictError("E-mail já cadastrado.") from error
        return user

    @translate_errors
    def get_by_id(self, user_id: str) -> User | None:
        document = self._collection.find_one({"_id": user_id})
        return self._to_entity(document) if document else None

    @translate_errors
    def list_all(self, *, limit: int = 50, skip: int = 0) -> list[User]:
        documents = self._collection.find().sort("created_at", -1).skip(skip).limit(limit)
        return [self._to_entity(document) for document in documents]

    @translate_errors
    def add_address(self, user_id: str, address: Address) -> User | None:
        document = self._collection.find_one_and_update(
            {"_id": user_id},
            {"$push": {"addresses": asdict(address)}},
            return_document=ReturnDocument.AFTER,
        )
        return self._to_entity(document) if document else None

    @translate_errors
    def delete(self, user_id: str) -> bool:
        result = self._collection.delete_one({"_id": user_id})
        return result.deleted_count > 0

    @staticmethod
    def _to_document(user: User) -> dict:
        return {
            "_id": user.id,
            "name": user.name,
            "email": user.email,
            "addresses": [asdict(address) for address in user.addresses],
            "created_at": user.created_at,
        }

    @staticmethod
    def _to_entity(document: dict) -> User:
        return User(
            id=document["_id"],
            name=document["name"],
            email=document["email"],
            addresses=tuple(
                Address(street=a["street"], city=a["city"], state=a["state"])
                for a in document.get("addresses", [])
            ),
            created_at=document["created_at"],
        )
