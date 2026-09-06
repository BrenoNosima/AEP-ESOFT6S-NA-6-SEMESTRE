# Roteiro do vídeo de demonstração (2–3 min)

Objetivo: apresentar problema, ODS, arquitetura inicial e a PoC executando, dentro
do tempo. Sugestão de divisão entre os 3 integrantes: uma seção cada + a demo junto.

## 1. Problema e ODS 12 — ~30s

- O que é o EcoMentor: chatbot que responde dúvidas do dia a dia sobre descarte,
  água e consumo consciente.
- ODS 12 (Consumo e Produção Responsáveis): cada resposta orienta descarte correto
  e redução de desperdício.
- Público: pessoa física querendo orientação rápida e confiável.

## 2. Arquitetura inicial — ~45s

- Mostrar o diagrama de [`architecture.md`](architecture.md).
- Pontos a falar: camadas (rotas → serviços → interfaces do domínio → infraestrutura);
  serviços dependem só de abstrações; Groq e MongoDB só aparecem na borda.
- Banco: uma única coleção `consultations`, documentos homogêneos ([`DocMongoDB.md`](DocMongoDB.md)).

## 3. Demonstração da PoC no Swagger (`/docs`) — ~60s

Pré-requisito: `.env` com `GROQ_API_KEY` e MongoDB no ar; `uvicorn app.main:app --reload`.

1. `POST /consultations` com `{"question": "Posso jogar óleo de cozinha na pia?", "category": "residuos"}`
   → 201 com a orientação gerada pela Groq.
2. `GET /consultations` → a consulta aparece na lista.
3. `GET /consultations/{id}` → busca a mesma consulta; mostrar um id inexistente → 404.
4. `DELETE /consultations/{id}` → 204; `GET` de novo → 404.
5. (Opcional) mostrar o documento no MongoDB Compass / `mongosh`.

## 4. Testes e cobertura — ~20s

- Rodar `pytest` e mostrar: todos verdes + linha "Total coverage: ~91%" (acima do
  mínimo de 70%).
- Mencionar que o CI roda o mesmo comando a cada push.

## Fechamento

- Versão desta entrega: tag `entrega-1`.
- O que vem na 2ª entrega: classificação automática de dúvidas, múltiplos agentes,
  modelagem com mais de uma coleção.
