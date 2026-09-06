# EcoMentor — backend

API FastAPI do EcoMentor. Visão geral do projeto e do problema/ODS no
[README da raiz](../README.md).

## Requisitos

- Python 3.12+
- (Opcional) MongoDB local para rodar os testes de integração reais
- Chave da Groq (<https://console.groq.com/keys>) para chamadas reais à LLM

## Instalação

```bash
python -m venv .venv
.venv/Scripts/activate          # Windows | Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env             # preencher GROQ_API_KEY e MONGODB_URI
```

Variáveis (`.env`, ver `.env.example`):

| Variável | Default | Uso |
|---|---|---|
| `GROQ_API_KEY` | — | credencial da Groq |
| `GROQ_MODEL` | `openai/gpt-oss-20b` | modelo usado no `ChatGroq` |
| `MONGODB_URI` | `mongodb://localhost:27017` | conexão do MongoDB |
| `MONGODB_DB_NAME` | `ecomentor` | nome do banco |
| `ENVIRONMENT` | `development` | `development` \| `production` |

## Executar

```bash
uvicorn app.main:app --reload
```

- `GET /health` — checagem simples
- `POST /consultations` — cria uma consulta (gera a resposta via Groq e persiste)
- `GET /consultations` — lista (mais recentes primeiro)
- `GET /consultations/{id}` — busca por id (404 se não existe)
- `DELETE /consultations/{id}` — remove (404 se não existe)

Swagger em `http://localhost:8000/docs`.

## Testes e cobertura

```bash
pytest
```

`pytest.ini` aplica `--cov=app --cov-report=term-missing --cov-fail-under=80`.
Detalhamento da suíte em [docs/testes.md](docs/testes.md).

## Estrutura

```
app/
  api/routes/          endpoints FastAPI (composition root das dependências)
  services/            regra de negócio (ConsultationService, SustainabilityService)
  domain/interfaces/   contratos abstratos (ConsultationRepository, LLMProvider)
  domain/models/       entidade Consultation
  domain/exceptions.py RepositoryError (falha de infraestrutura de dados)
  repositories/        MongoConsultationRepository
  llm/providers/       GroqProvider (real), FakeLLMProvider (testes)
  database/            conexão MongoDB
  core/                configuração (pydantic-settings)
tests/
  unit/                testes rápidos e determinísticos (mongomock, fakes)
  integration/         API via TestClient; MongoDB real (pulado se indisponível)
docs/                  documentação técnica
```
