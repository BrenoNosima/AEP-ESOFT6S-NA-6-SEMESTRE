# 1ª Entrega da AEP — evidências

Mapa de cada critério da rubrica (`.claude/skills/aep-rubric/SKILL.md`) para a
evidência no repositório.

| Critério | Evidência | Onde |
|---|---|---|
| Problema e alinhamento ao ODS 12 | Problema, público e relação com o ODS 12 descritos. | [`README.md`](../../README.md) |
| 1ª versão funcional da PoC | App sobe e executa o fluxo Usuário → API → serviço → LLM → MongoDB → resposta. | `app/main.py`, `app/api/routes/consultations.py`; demo via `/docs` |
| Banco NoSQL (coleção única, homogênea, CRUD) | Coleção única `consultations`, documentos de 5 campos, CRUD completo. | `app/repositories/mongo_consultation_repository.py`, [`DocMongoDB.md`](DocMongoDB.md) |
| POO e organização | Camadas + ABCs (`ConsultationRepository`, `LLMProvider`) + injeção de dependência; domínio sem infraestrutura. | [`architecture.md`](architecture.md) |
| GitHub e versionamento | Histórico incremental, 1 tarefa ≈ 1 commit, PRs. | histórico git; tag `entrega-1` |
| Testes automatizados | 38 testes (unit + integração), executáveis com um comando. | `tests/`, [`testes.md`](testes.md) |
| Cobertura ≥ 70% | `pytest` aplica `--cov-fail-under=80`; CI reproduz. | `pytest.ini`, `.github/workflows/tests.yml` |
| Vídeo de demonstração (2–3 min) | Roteiro pronto. | [`roteiro-video.md`](roteiro-video.md) |

## Organização mínima do repositório (seção 9 da rubrica)

- `README.md` na raiz ✔
- Código-fonte da PoC (`backend/app/`) ✔
- Documentação técnica (`backend/docs/`) ✔
- Testes automatizados (`backend/tests/`) ✔
- Evidência reproduzível de cobertura (`pytest.ini` + CI) ✔
- Identificação da versão: tag **`entrega-1`** ✔

## Escopo travado (não faz parte desta entrega)

Segunda coleção, relacionamento entre coleções, subdocumentos, LangGraph, múltiplos
agentes, classificação automática, segundo provider real de LLM, front-end.

## Pendências / handoff

### Pessoa 1 — rota PATCH de categoria (opcional; completa o CRUD na borda)

O `update_category` já existe na interface, no `MongoConsultationRepository` e nos
testes. Falta expor na API:

1. `ConsultationService.update_consultation_category(consultation_id, category) -> Consultation | None`
   delegando a `self._repository.update_category(...)`.
2. Em `api/routes/consultations.py`: schema `ConsultationCategoryUpdate(BaseModel)` com
   `category: str` e `@router.patch("/{consultation_id}", response_model=ConsultationResponse)`
   chamando o serviço; `HTTPException(404)` se `None`; manter o `except RepositoryError` → 503.
3. Em `tests/integration/test_consultations_api.py`: implementar `update_category` no
   `InMemoryConsultationRepository` (hoje `raise NotImplementedError`) com `dataclasses.replace`;
   testes de 200 e 404.

Commit de referência: `feat: expor atualização de categoria na API de consultations`.

### Robustez — já aplicado

- `PyMongoError` (Mongo fora do ar) → `RepositoryError` → **503** nas rotas de `consultations`.
- Falha ao construir o `ChatGroq` → `RuntimeError` → 502.
- `get_database()` com `serverSelectionTimeoutMS=5000` (evita travar 30 s).
- `GET /health` faz `ping` no MongoDB → 200 / 503.

### Robustez — ainda pendente (handoff)

- `get_llm_provider` reconstrói o `ChatGroq` a cada request — cachear (`@lru_cache`).
- `tests/integration/test_consultations_api.py` usa `app.dependency_overrides` no import
  sem limpar; migrar para fixture com `app.dependency_overrides.clear()` no teardown.
- Os testes da Pessoa 1 ainda definem `FakeLLMProvider` localmente; podem importar de
  `app/llm/providers/fake_provider.py`.
