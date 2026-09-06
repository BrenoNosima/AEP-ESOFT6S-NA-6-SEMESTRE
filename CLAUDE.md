# EcoMentor — AEP Engenharia de Software (6S)

## O que é

Chatbot de orientação em sustentabilidade. Usuário manda uma dúvida (ex: "posso jogar óleo de cozinha na pia?"), a API consulta uma LLM para gerar uma orientação educativa e salva a interação no MongoDB.

- **ODS:** 12 — Consumo e Produção Responsáveis.
- **Fluxo:** Usuário → FastAPI (`api/router.py`) → `ConsultationService` → `SustainabilityService` → `LLMProvider` (Groq) → `MongoConsultationRepository` (MongoDB) → resposta JSON.
- **Trabalho da faculdade:** `AEP_ESoft_6S.pdf`. **Divisão de papéis:** `EcoMentor_Chatbot_Divisao_3_Pessoas.pdf`.

## Escopo travado da 1ª entrega — não expandir

O enunciado da AEP exige, para o 1º semestre, **uma única coleção NoSQL** com objetos homogêneos e CRUD básico. Por isso, nesta entrega:

- Só existe a coleção `consultations`. Não criar uma segunda coleção nem relacionar coleções (isso é requisito da 2ª entrega).
- Só existe **um** provider de LLM real: Groq (`langchain-groq`). Não implementar Gemini/OpenAI/múltiplos providers agora — a interface `LLMProvider` já permite isso depois.
- Sem LangGraph, sem múltiplos agentes, sem classificação automática de dúvidas. Isso é escopo da 2ª entrega.
- Sem front-end. A demonstração é pelo Swagger (`/docs`) do FastAPI.
- Nunca commitar `.env` ou chaves de API — só `.env.example`. O mesmo vale para `.claude/settings.local.json`, se alguém criar um.

Se alguma tarefa parecer exigir essas coisas, é sinal de que ela pertence à 2ª entrega, não a esta.

## Arquitetura (camadas em `backend/app`)

```
api/router.py         -> endpoints FastAPI de consultations (recebe request, chama service, devolve JSON)
api/routes/           -> outros endpoints FastAPI (ex: health)
api/services/         -> regra de negócio (ConsultationService, SustainabilityService)
api/repositories/     -> implementação concreta dos repositories (Mongo)
domain/interfaces/    -> contratos abstratos (ConsultationRepository, LLMProvider)
domain/models/        -> entidades (Consultation)
llm/providers/        -> implementação concreta dos LLM providers (Groq, Fake)
database/             -> conexão com MongoDB
core/                 -> configuração (variáveis de ambiente, settings)
```

Regra de dependência: rotas dependem de services; services dependem só das **interfaces** (`ConsultationRepository`, `LLMProvider`), nunca das implementações concretas diretamente — isso é o que sustenta o critério de POO/abstração da rubrica. `domain/interfaces` e `domain/models` continuam fora de `api/` justamente para não misturar contrato abstrato com camada HTTP.

**Divisão entre os 3 integrantes** (ver PDF de divisão para detalhes):
- Pessoa 1 — Backend e API: `main.py`, `api/router.py`, `api/routes/`, `api/services/consultation_service.py`.
- Pessoa 2 — LLM e LangChain: `llm/providers/`, `api/services/sustainability_service.py`.
- Pessoa 3 — MongoDB e NoSQL: `database/mongodb.py`, `api/repositories/`, `domain/models/consultation.py`.

## Como trabalhamos: 1 tarefa do Kanban = 1 commit

O quadro está no Notion: https://app.notion.com/p/3cc93299daff8196b82eddaf4b420ed0. Cada card tem uma "Commit de referência" — é a mensagem de commit esperada quando a tarefa for concluída. Ao terminar uma tarefa:

1. Rodar os testes relacionados localmente.
2. Commitar usando o padrão `tipo: descrição curta no infinitivo`, com `tipo` em `feat`, `test`, `docs` ou `chore` (Conventional Commits simplificado).
3. Mover o card para "Concluído" no Notion.

Isso é o que vira evidência de "GitHub e versionamento" (histórico de commits organizado) na correção.

## Rodando o projeto

**Com Docker** (sobe API + MongoDB): na raiz do repo, `Copy-Item backend/.env.example backend/.env` (preencher `GROQ_API_KEY`) e `docker compose up --build`. Ver `docker-compose.yml`.

**Sem Docker** (venv local):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell (cmd: .venv\Scripts\activate.bat; Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
Copy-Item .env.example .env    # preencher GROQ_API_KEY e MONGODB_URI
uvicorn app.main:app --reload
```

`&&` não funciona no Windows PowerShell 5.1 — rode uma linha por vez. Sem ativar o venv, use `python -m` (ex.: `python -m uvicorn app.main:app --reload`).

Swagger em `http://localhost:8000/docs`.

## Testes e cobertura

```bash
cd backend
pytest
```

O `pytest.ini` já aplica `--cov=app --cov-report=term-missing --cov-fail-under=80`. A rubrica exige no mínimo 70%; o projeto trava em 80%. O CI (`.github/workflows/tests.yml`, na raiz) roda o mesmo `pytest` com um serviço `mongo:7`, então lá os testes de integração real também executam — é a evidência reproduzível que a rubrica pede.

Testes que dependem da LLM devem usar `FakeLLMProvider` (`app/llm/providers/fake_provider.py`), nunca a API real da Groq — mantém os testes determinísticos, rápidos e sem custo.

## Ferramentas de apoio em `.claude/`

Ver [.claude/README.md](.claude/README.md) para o que cada arquivo faz. Resumo rápido:

- `/next-task` — mostra a próxima tarefa do Kanban a implementar, na ordem certa.
- `/check-scope` — checagem rápida contra as regras de escopo desta seção.
- Subagente `rubric-auditor` — audita o repo inteiro contra a rubrica da 1ª entrega (rodar antes da tag `entrega-1`).
- Subagente `coverage-check` — roda `pytest --cov` e resume o que falta para bater 70%.
