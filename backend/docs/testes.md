# Testes e cobertura de código

## Objetivo

A suíte foi preparada para cobrir exatamente **80% das linhas executáveis** do
backend atual. O relatório considera todos os arquivos Python dentro de `app`.

O projeto possui 50 statements (linhas que o Python pode executar). Os testes
passam por 40 deles:

```text
40 linhas cobertas / 50 linhas executáveis = 80%
```

Arquivos vazios aparecem com 100% no relatório porque ainda não possuem linhas
executáveis. Eles não aumentam nem diminuem o resultado total.

## O que cada teste verifica

- `test_health.py`: chama `GET /health` e confere o status HTTP e o JSON.
- `test_sustainability_service.py`: usa um provider falso para conferir a
  resposta e a montagem do prompt, sem gastar créditos de uma API real.
- `test_llm_provider.py`: confere se `GroqProvider` segue o contrato
  `LLMProvider` usado pela aplicação.

Os testes não chamam a Groq e não precisam de chave de API. Isso deixa o
resultado rápido, gratuito e igual em qualquer computador.

## Como executar

Dentro da pasta `backend`, instale as dependências e rode:

```bash
python -m pip install -r requirements.txt
python -m pytest
```

O arquivo `pytest.ini` já ativa a cobertura, mostra as linhas não executadas e
faz o comando falhar se o total ficar abaixo de 80%.

## Como ler o relatório

- `Stmts`: quantidade de statements do arquivo.
- `Miss`: statements que nenhum teste executou.
- `Cover`: percentual coberto.
- `Missing`: números das linhas que ainda não foram executadas.

Como o código ainda está em construção, novas linhas podem alterar o percentual.
Nesse caso, devem ser criados testes para o novo comportamento antes da entrega.
