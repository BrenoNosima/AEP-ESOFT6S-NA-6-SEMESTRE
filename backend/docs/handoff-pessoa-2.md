# Handoff da Pessoa 2 — LLM e LangChain

Este documento registra o que foi implementado pela Pessoa 2 na 2ª entrega e o
contrato que a Pessoa 1 deve usar ao integrar o fluxo HTTP. Ele não substitui a
documentação final da entrega.

## Arquivos sob responsabilidade da Pessoa 2

- `app/llm/providers/`
- `app/api/services/sustainability_service.py`
- `tests/unit/test_groq_provider.py`
- `tests/unit/test_llm_provider.py`
- `tests/unit/test_sustainability_service.py`

## Classificação automática

O método disponível é:

```python
category = sustainability_service.classify_category(question)
```

Contrato:

- Recebe a pergunta do usuário como `str`.
- Solicita à LLM somente uma das categorias reconhecidas pelo domínio.
- Normaliza espaços nas extremidades e diferenças entre maiúsculas e minúsculas.
- Retorna uma instância de `Category`, não uma string livre.
- Levanta `LLMProviderError` quando a resposta não é textual ou não corresponde a
  uma categoria válida.

Categorias aceitas:

- `residuos`
- `agua`
- `energia`
- `consumo`
- `geral`

A Pessoa 1 deve chamar esse método somente quando a categoria não vier no request.
A validação final continua sendo feita pelo enum `Category`.

Exemplo de integração, apenas como referência:

```python
category = request_category
if category is None:
    category = sustainability_service.classify_category(question)
```

## Orientação contextualizada

O método disponível é:

```python
answer = sustainability_service.generate_guidance(
    question,
    city="Maringá",
    state="PR",
)
```

Contrato:

- `city` e `state` são argumentos nomeados e opcionais.
- Quando ambos são informados, o prompt inclui a cidade e o estado do usuário.
- Quando a localização não é informada, o prompt registra explicitamente essa
  ausência e a orientação continua funcionando.
- O prompt proíbe inventar endereços, pontos de coleta, horários de atendimento e
  regras municipais.
- Sem informação municipal confiável, a LLM deve reconhecer a limitação e indicar
  os canais oficiais da prefeitura.
- Erros do provider continuam sendo propagados como `LLMProviderError`.

A Pessoa 1 é responsável por buscar o usuário e seu endereço principal antes de
chamar esse método. A Pessoa 2 não acessa `UserRepository` diretamente.

## Fluxo esperado na integração

1. A rota recebe `user_id`, pergunta e categoria opcional.
2. `ConsultationService` busca o usuário por meio de `UserRepository`.
3. Se a categoria estiver ausente, chama `classify_category`.
4. Obtém cidade e estado do endereço principal do usuário.
5. Chama `generate_guidance` com pergunta, cidade e estado.
6. Persiste a consulta com a categoria final, `user_id` e o snapshot da localização.

Os passos de rota, busca do usuário e orquestração pertencem à Pessoa 1. Modelos,
repositórios MongoDB, relacionamento e snapshot da localização pertencem à Pessoa 3.

## Testes

Os testes da Pessoa 2 não chamam a API real da Groq. Eles usam
`FakeLLMProvider` ou mocks para permanecerem determinísticos e sem custo.

Coberturas verificadas:

- Todas as categorias válidas.
- Normalização de caixa e espaços.
- Categoria desconhecida e resposta em formato inválido.
- Propagação de falhas do provider.
- Inclusão da pergunta e das categorias permitidas no prompt.
- Contextualização com cidade e estado.
- Comportamento sem localização.
- Restrições contra informações municipais inventadas.

Para executar toda a suíte:

```bash
cd backend
pytest
```

Última validação local, com MongoDB do Docker ativo: 82 testes aprovados, nenhum
teste pulado e cobertura total de 92,42%. Esse número pode mudar conforme novas
funcionalidades forem integradas; o requisito permanente é manter pelo menos 80%
configurado no projeto.

## Fora do escopo da Pessoa 2

- Tornar `category` opcional no schema HTTP.
- Criar ou alterar rotas de usuários e consultas.
- Buscar o usuário ou escolher seu endereço principal.
- Alterar `ConsultationService` e a injeção de dependências.
- Criar coleções, índices, relacionamentos ou agregações MongoDB.
- Adicionar outro provider real, LangGraph, múltiplos agentes ou frontend.
