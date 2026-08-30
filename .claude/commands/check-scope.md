---
description: Checa rapidamente sinais de que o projeto saiu do escopo travado da 1ª entrega (ver CLAUDE.md).
argument-hint: ""
---

Rode, a partir da raiz do repositório, e reporte o que encontrar (sem corrigir nada automaticamente, só listar):

1. `git status --short` — algo além do esperado no working tree?
2. Existe mais de uma coleção Mongo referenciada em `backend/app/` (procure por `.consultations` e qualquer outro nome de coleção)?
3. Existe mais de um provider de LLM real além de `gemini_provider.py` e `fake_provider.py` em `backend/app/llm/providers/`?
4. A pasta `backend/app/agents/` ou qualquer referência a LangGraph voltou a existir?
5. Existe algum `.env` (não `.env.example`) rastreado pelo git (`git ls-files | grep -E "\.env$"`)?
6. `backend/.gitignore` está vazio ou ausente?

Para cada item, diga OK ou aponte o problema encontrado. Isso é uma checagem manual e rápida — para uma auditoria completa contra a rubrica, use o agente `rubric-auditor`.
