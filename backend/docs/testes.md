# Testes e cobertura

## Como executar

```bash
cd backend
pip install -r requirements.txt
pytest
```

`pytest.ini` já aplica `--cov=app --cov-report=term-missing --cov-fail-under=80`:
a cobertura é exibida a cada execução e o comando **falha** se o total cair abaixo
de 80% (a rubrica exige no mínimo 70%). O mesmo comando roda no CI
(`.github/workflows/tests.yml`).

Nenhum teste chama a API real da Groq nem precisa de chave: a LLM é substituída pelo
`FakeLLMProvider` (`app/llm/providers/fake_provider.py`). Isso deixa a suíte rápida,
gratuita e determinística.

## Suíte

**40 testes** (36 executados, 4 pulados quando não há MongoDB local).

### Unitários — `tests/unit/`

| Arquivo | Cobre |
|---|---|
| `test_consultation_service.py` | `ConsultationService` orquestrando LLM + repositório, com `FakeLLMProvider` e um repositório em memória. |
| `test_sustainability_service.py` | montagem do prompt e uso do `LLMProvider` (via `FakeLLMProvider` compartilhado). |
| `test_groq_provider.py` | `GroqProvider` com `ChatGroq` mockado: resposta ok, erro no `invoke` → `RuntimeError`, conteúdo não-string, falha ao construir o client. |
| `test_llm_provider.py` | `GroqProvider` respeita o contrato `LLMProvider`. |
| `test_mongo_consultation_repository.py` | CRUD completo via `mongomock` (`tz_aware=True`), ordenação por `created_at`, casos "não encontrado", e `PyMongoError` → `RepositoryError`. |
| `test_database.py` | `get_database()` devolve o `Database` com o nome configurado (cobre `app/database/mongodb.py`). |

### Integração — `tests/integration/`

| Arquivo | Cobre |
|---|---|
| `test_health.py` | `GET /health` com `get_database` mockado: 200 quando o `ping` responde, 503 quando levanta `PyMongoError`. |
| `test_consultations_api.py` | rotas de `consultations` via `TestClient`, com `app.dependency_overrides` trocando o serviço por um repositório em memória compartilhado. Cobre 201/200/404/204 e 503 quando o repositório levanta `RepositoryError`. |
| `test_mongodb.py` | round-trip contra um MongoDB **real** (`MONGODB_URI`, banco `ecomentor_test`). Pulado automaticamente (`pytest.mark.skipif`) se não houver MongoDB acessível. |

## Padrões usados

- **`FakeLLMProvider`** para toda dependência de LLM.
- **`mongomock`** nos testes unitários do repositório; **MongoDB real** só na
  integração opcional.
- **`app.dependency_overrides`** para injetar dublês nas rotas sem subir infraestrutura.
- Pirâmide de testes: muitos unitários rápidos na base, poucos de integração no topo.

## Como ler o relatório

- `Stmts`: statements do arquivo · `Miss`: não executados · `Cover`: % coberto ·
  `Missing`: linhas não executadas.
- Ao adicionar comportamento novo, escrever o teste correspondente antes de commitar —
  o gate de 80% (`--cov-fail-under`) quebra o build caso contrário.
