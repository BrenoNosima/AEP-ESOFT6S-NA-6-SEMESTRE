---
description: Checa rapidamente sinais de que o projeto saiu do escopo da 2ª entrega (ver CLAUDE.md).
argument-hint: ""
---

Rode, a partir da raiz do repositório, e reporte o que encontrar (sem corrigir nada automaticamente, só listar):

1. `git status --short` — algo além do esperado no working tree?
2. Coleções Mongo referenciadas em `backend/app/` (procure `_COLLECTION_NAME` e `database[`): devem ser exatamente `users` e `consultations`. Uma coleção a mais precisa de justificativa no Kanban.
3. Existe mais de um provider de LLM real além de `groq_provider.py` e `fake_provider.py` em `backend/app/llm/providers/`?
4. A pasta `backend/app/agents/` ou qualquer referência a LangGraph existe?
5. Existe algum front-end (pasta `frontend/`, arquivos `.html`/`.tsx`/`.vue`)?
6. Existe algum `.env` (não `.env.example`) rastreado pelo git (`git ls-files | grep -E "\.env$"`)?
7. Algum commit desde a tag `entrega-1` traz `Co-Authored-By` de ferramenta de IA ou foge do padrão `tipo: descrição` (`git log entrega-1..HEAD --format="%s%n%b"`)?

Para cada item, diga OK ou aponte o problema encontrado. Isso é uma checagem manual e rápida — para uma auditoria completa contra a rubrica, use o agente `rubric-auditor`.
