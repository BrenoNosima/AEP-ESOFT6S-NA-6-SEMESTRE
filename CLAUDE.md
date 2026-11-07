# EcoMentor — AEP Engenharia de Software (6S)

## O que é

Chatbot de orientação em sustentabilidade. Usuário manda uma dúvida (ex: "posso jogar óleo de cozinha na pia?"), a API consulta uma LLM para gerar uma orientação educativa e salva a interação no MongoDB.

- **ODS:** 12 — Consumo e Produção Responsáveis.
- **Fluxo (2ª entrega):** Usuário → FastAPI (`api/routes/`) → `ConsultationService` → `UserRepository` (busca o usuário e o endereço) + `SustainabilityService` → `LLMProvider` (Groq) → `ConsultationRepository` (MongoDB) → resposta JSON.
- **Trabalho da faculdade:** `AEP_ESoft_6S.pdf`. **Divisão de papéis:** `EcoMentor_Chatbot_Divisao_3_Pessoas.pdf`.
- **1ª entrega:** concluída, tag `entrega-1` (commit `2f5d256`). Não reescrever esse histórico.

## Escopo da 2ª entrega — o que entra e o que continua fora

O enunciado (seção 8, 2º semestre) exige **múltiplas coleções**, **relacionamento entre coleções** e **pelo menos uma coleção com objetos complexos** (documentos aninhados ou listas de subdocumentos). A rubrica da 2ª entrega também cobra ausência de duplicação/acoplamento, quadro de tarefas, documentação completa (incluindo estrutura do banco) e versão final identificável.

**Entra:**
- Coleção `users` com `addresses: [{street, city, state}]` (lista de subdocumentos), e-mail com índice único.
- Coleção `consultations` com `user_id` (referência a `users._id`) e subdocumento `location: {city, state}` (snapshot do endereço usado na resposta).
- Integridade referencial na aplicação: criar consulta exige usuário existente (404); remover usuário remove as consultas dele (cascata).
- Agregação `$group` por categoria (`GET /users/{id}/consultations/summary`).
- Orientação contextualizada pela cidade do usuário e **classificação automática da categoria** pela LLM quando ela não vier no request.

**Continua fora (não é pedido pelo PDF):**
- Segundo provider de LLM real. Só Groq (`langchain-groq`); a interface `LLMProvider` já permite trocar.
- LangGraph, múltiplos agentes, pasta `app/agents/`.
- Front-end. A demonstração é pelo Swagger (`/docs`).
- Nunca commitar `.env` ou chaves de API — só `.env.example`. O mesmo vale para `.claude/settings.local.json`.

Se alguma tarefa parecer exigir algo da lista "continua fora", pare e confirme com o time antes.

## Arquitetura (camadas em `backend/app`)

```
api/routes/           -> endpoints FastAPI (consultations, users, health)
api/dependencies.py   -> composition root: factories Depends que montam services com implementações concretas
api/schemas.py        -> modelos Pydantic de request/response (só na borda HTTP)
api/services/         -> regra de negócio (ConsultationService, UserService, SustainabilityService)
api/repositories/     -> implementação concreta dos repositories (Mongo)
domain/interfaces/    -> contratos abstratos (ConsultationRepository, UserRepository, LLMProvider)
domain/models/        -> entidades (Consultation, User, Address, Location, Category)
domain/exceptions.py  -> erros de domínio (RepositoryError, NotFoundError, ...) traduzidos em HTTP no main.py
llm/providers/        -> implementação concreta dos LLM providers (Groq, Fake)
database/             -> conexão com MongoDB
core/                 -> configuração (variáveis de ambiente, settings)
```

Regra de dependência: rotas dependem de services; services dependem só das **interfaces** (`ConsultationRepository`, `UserRepository`, `LLMProvider`), nunca das implementações concretas — isso é o que sustenta o critério de POO/abstração da rubrica. O wiring concreto fica só em `api/dependencies.py`. Erros de domínio viram status HTTP via `exception_handlers` no `main.py`, não com `try/except` repetido em cada rota.

**Divisão entre os 3 integrantes** (ver PDF de divisão para detalhes):
- Pessoa 1 — Backend e API: `main.py`, `api/routes/`, `api/dependencies.py`, `api/schemas.py`, `api/services/consultation_service.py`, `api/services/user_service.py`.
- Pessoa 2 — LLM e LangChain: `llm/providers/`, `api/services/sustainability_service.py`.
- Pessoa 3 — MongoDB e NoSQL: `database/mongodb.py`, `api/repositories/`, `domain/models/`, `domain/interfaces/*_repository.py`.

## Como trabalhamos: 1 tarefa do Kanban = 1 commit

O quadro está no Notion, página https://app.notion.com/p/3cc93299daff8196b82eddaf4b420ed0. A 2ª entrega usa a database **"Kanban — Entrega 2"** (https://app.notion.com/p/6f6980145eae40c48ba937b14c8e9310, visualização "Quadro"). Cada card tem uma "Commit de referência" — é a mensagem de commit esperada quando a tarefa for concluída. Ao começar, mover o card para "Em Andamento". Ao terminar:

1. Rodar os testes relacionados localmente (`pytest` precisa continuar verde e ≥ 80%).
2. Commitar **exatamente uma vez por card**, no padrão `tipo: descrição curta no infinitivo`, com `tipo` em `feat`, `fix`, `refactor`, `test`, `docs` ou `chore`. Não juntar várias tarefas num commit.
3. Mover o card para "Concluído" no Notion.

Commits, PRs, tags e releases **não** levam linha de co-autoria nem menção a ferramentas de IA — o histórico é da equipe.

Isso é o que vira evidência de "GitHub e versionamento" e "Metodologia de trabalho" na correção.

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

- `/next-task` — mostra a próxima tarefa do Kanban da 2ª entrega, na ordem certa.
- `/check-scope` — checagem rápida contra as regras de escopo da 2ª entrega.
- Subagente `rubric-auditor` — audita o repo inteiro contra a rubrica da 2ª entrega (rodar antes da tag `entrega-2`).
- Subagente `coverage-check` — roda `pytest --cov` e resume o que falta para bater 70%.
