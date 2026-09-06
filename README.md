# EcoMentor

Chatbot de orientação em sustentabilidade. O usuário envia uma dúvida do dia a dia
(ex.: *"posso jogar óleo de cozinha na pia?"*); a API consulta uma LLM para gerar uma
orientação educativa e prática, e registra a interação no MongoDB.

**AEP — Engenharia de Software (6º semestre). 1ª entrega.**

## Problema e ODS

Muita gente quer adotar hábitos de consumo mais responsáveis, mas não sabe o
descarte ou a prática correta para cada caso, e a informação está espalhada.
O EcoMentor centraliza essa orientação num canal único, em linguagem simples.

- **ODS 12 — Consumo e Produção Responsáveis.** Cada resposta incentiva descarte
  correto, redução de desperdício e escolhas de consumo conscientes.
- **Público:** pessoas físicas buscando orientação rápida sobre resíduos, água e consumo.

## Arquitetura

```
Usuário / Swagger
      │
      ▼
FastAPI  (app/api/routes)         ── recebe request, injeta dependências, traduz erro em HTTP
      │
      ▼
ConsultationService (app/services) ── orquestra: pede orientação à LLM e persiste
      ├─ SustainabilityService ──► LLMProvider (Groq)          app/llm/providers
      └─ ConsultationRepository (ABC) ──► MongoConsultationRepository ──► MongoDB
                                          app/repositories            coleção única `consultations`
```

Regra de dependência: rotas → serviços → **interfaces** do domínio. As implementações
concretas (Groq, MongoDB) só são conhecidas na borda (`app/api/routes`). Detalhes em
[backend/docs/architecture.md](backend/docs/architecture.md) e
[backend/docs/DocMongoDB.md](backend/docs/DocMongoDB.md).

## Como rodar

```bash
cd backend
python -m venv .venv && .venv/Scripts/activate      # Windows (Linux: source .venv/bin/activate)
pip install -r requirements.txt
cp .env.example .env                                 # preencher GROQ_API_KEY e MONGODB_URI
uvicorn app.main:app --reload
```

Swagger interativo em `http://localhost:8000/docs`.

## Como testar

```bash
cd backend
pytest
```

`pytest.ini` já ativa cobertura e falha o build abaixo de 80%. Os testes usam
`FakeLLMProvider` e `mongomock` — não precisam de chave da Groq nem de MongoDB no ar
(os testes de integração contra MongoDB real são pulados automaticamente se não houver banco).
Mais detalhes em [backend/docs/testes.md](backend/docs/testes.md).

## Versão da entrega

1ª entrega identificada pela tag **`entrega-1`**.

## Repositório

<https://github.com/BrenoNosima/AEP-ESOFT6S-NA-6-SEMESTRE>
