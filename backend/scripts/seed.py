"""Popula o MongoDB com dados de demonstração (usuários, endereços e consultas).

Uso (a partir de `backend/`, com o MongoDB no ar):

    python -m scripts.seed

É idempotente: ids e e-mails são fixos, então rodar de novo não duplica nada.
Não chama a LLM: as respostas são texto fixo, então funciona sem GROQ_API_KEY.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pymongo.database import Database

from app.api.repositories.mongo_consultation_repository import MongoConsultationRepository
from app.api.repositories.mongo_user_repository import MongoUserRepository
from app.database.mongodb import get_database
from app.domain.exceptions import ConflictError
from app.domain.models.consultation import Consultation
from app.domain.models.location import Location
from app.domain.models.user import Address, User

_BASE_DATE = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)

_USERS = [
    User(
        id="seed-user-ana",
        name="Ana Souza",
        email="ana.souza@email.com",
        addresses=(
            Address(street="Rua das Flores, 100", city="Maringá", state="PR"),
            Address(street="Av. Brasil, 500", city="Curitiba", state="PR"),
        ),
        created_at=_BASE_DATE,
    ),
    User(
        id="seed-user-bruno",
        name="Bruno Lima",
        email="bruno.lima@email.com",
        addresses=(Address(street="Rua Verde, 45", city="Londrina", state="PR"),),
        created_at=_BASE_DATE,
    ),
]

# (id, user_id, pergunta, categoria, resposta, cidade, estado)
_CONSULTATIONS = [
    (
        "seed-consulta-1",
        "seed-user-ana",
        "Posso jogar óleo de cozinha na pia?",
        "residuos",
        "Não. Guarde o óleo usado em uma garrafa PET e leve a um ponto de coleta de Maringá.",
        "Maringá",
        "PR",
    ),
    (
        "seed-consulta-2",
        "seed-user-ana",
        "Como separar o lixo reciclável em casa?",
        "residuos",
        "Separe papel, plástico, vidro e metal, limpos e secos, e entregue à coleta seletiva.",
        "Maringá",
        "PR",
    ),
    (
        "seed-consulta-3",
        "seed-user-ana",
        "Como economizar água no banho?",
        "agua",
        "Reduza o tempo do banho para 5 minutos e feche o registro ao se ensaboar.",
        "Maringá",
        "PR",
    ),
    (
        "seed-consulta-4",
        "seed-user-bruno",
        "Vale a pena trocar lâmpadas por LED?",
        "energia",
        "Sim. LEDs consomem até 80% menos energia e duram muito mais que as incandescentes.",
        "Londrina",
        "PR",
    ),
    (
        "seed-consulta-5",
        "seed-user-bruno",
        "Como reduzir o consumo de plástico descartável?",
        "consumo",
        "Use sacola retornável, garrafa reutilizável e prefira produtos a granel.",
        "Londrina",
        "PR",
    ),
]


def seed(database: Database) -> dict[str, int]:
    """Insere o que ainda não existe e devolve quantos usuários/consultas foram criados."""
    users = MongoUserRepository(database)
    consultations = MongoConsultationRepository(database)
    created = {"users": 0, "consultations": 0}

    for user in _USERS:
        try:
            users.save(user)
            created["users"] += 1
        except ConflictError:
            pass  # e-mail já cadastrado: seed já rodou

    for index, (cid, user_id, question, category, answer, city, state) in enumerate(
        _CONSULTATIONS
    ):
        if consultations.get_by_id(cid) is not None:
            continue
        consultations.save(
            Consultation(
                id=cid,
                user_id=user_id,
                question=question,
                category=category,
                answer=answer,
                location=Location(city=city, state=state),
                created_at=_BASE_DATE + timedelta(days=index + 1),
            )
        )
        created["consultations"] += 1

    return created


def main() -> None:
    created = seed(get_database())
    print(
        f"Seed concluído: {created['users']} usuário(s) e "
        f"{created['consultations']} consulta(s) criados."
    )


if __name__ == "__main__":
    main()
