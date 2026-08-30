# `.claude/` — configuração do Claude Code para este projeto

Esta pasta é lida automaticamente pelo Claude Code sempre que alguém do time abrir uma sessão neste repositório. Ela existe para que os três integrantes trabalhem com o mesmo contexto e as mesmas regras, independente de quem estiver digitando.

| Arquivo/pasta | Para que serve |
|---|---|
| `settings.json` | Permissões e configurações **compartilhadas pelo time** (comitado no git). |
| `settings.local.json` | Overrides **pessoais** de cada integrante (não existe por padrão — se você criar o seu, ele **não pode ser commitado**, ver abaixo). |
| `agents/` | Subagentes especializados para tarefas deste projeto (ex: auditar a rubrica da AEP, checar cobertura). |
| `commands/` | Comandos de barra (`/nome`) específicos do fluxo deste projeto. |
| `skills/` | Conhecimento de referência que o Claude carrega sob demanda (ex: a rubrica completa da 1ª entrega). |

## Importante: `settings.local.json`

Se você criar um `.claude/settings.local.json` na sua máquina (para preferências só suas), **garanta que ele está no `.gitignore`** antes do primeiro commit real do projeto (tarefa "Higienizar .gitignore" do Kanban). O mesmo vale para qualquer `.env` — nunca comitar chave de API ou string de conexão do Mongo.

## O que tem aqui hoje

- **`agents/rubric-auditor.md`** — roda uma auditoria manual do repositório contra os critérios da 1ª entrega da AEP e as regras de escopo do `CLAUDE.md` (coleção única, sem LangGraph, etc). Útil antes de marcar uma tarefa como concluída ou antes de criar a tag `entrega-1`.
- **`agents/coverage-check.md`** — roda `pytest --cov` e resume o que está abaixo dos 70% exigidos.
- **`commands/next-task.md`** (`/next-task`) — consulta o Kanban no Notion e diz qual é a próxima tarefa a implementar, na ordem correta de dependência.
- **`commands/check-scope.md`** (`/check-scope`) — checagem rápida (grep) por sinais de que o projeto saiu do escopo da 1ª entrega (segunda coleção, segundo provider de LLM, pasta `agents/` do LangGraph, segredos commitados).
- **`skills/aep-rubric/`** — a rubrica de avaliação da 1ª entrega, transcrita do PDF da AEP, para qualquer agente/skill referenciar sem depender de memória.
