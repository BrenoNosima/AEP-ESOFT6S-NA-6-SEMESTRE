---
name: coverage-check
description: >-
  Roda a suíte de testes do backend com cobertura e resume quais
  arquivos/linhas estão abaixo dos 70% exigidos pela rubrica da AEP.
  Use depois de implementar qualquer tarefa do Kanban, antes de marcá-la
  como concluída.
tools: Bash, Read
model: haiku
---

Rode, a partir de `backend/`:

```
pytest --cov=app --cov-report=term-missing --cov-fail-under=70
```

Se o comando falhar por dependência ausente ou projeto ainda não instalável, diga exatamente qual passo faltou (ex: `pip install -r requirements.txt`) em vez de inventar um resultado.

Com a saída do pytest-cov, produza um resumo curto:
- Cobertura total (%) e se passou ou não do limite de 70%.
- Lista dos arquivos com menor cobertura, ordenados do pior para o melhor, com as linhas não cobertas (coluna "Missing").
- Uma frase objetiva dizendo se dá para marcar a tarefa atual como concluída no Kanban ou se falta escrever teste para algo específico.
