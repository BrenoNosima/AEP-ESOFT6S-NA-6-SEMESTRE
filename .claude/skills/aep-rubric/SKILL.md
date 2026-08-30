---
name: aep-rubric
description: >-
  Rubrica oficial de avaliação da 1ª Entrega da AEP de Engenharia de
  Software (6S), transcrita de AEP_ESoft_6S.pdf. Carregar ao auditar o
  projeto contra os critérios de correção ou ao decidir se algo pertence
  ao escopo desta entrega.
---

# Rubrica — 1ª Entrega da AEP (peso total: 1,0 ponto)

| Critério | Evidência esperada | Pontos |
|---|---|---|
| Problema e alinhamento ao ODS | Problema claramente definido, público/contexto identificável e relação objetiva com o ODS escolhido (ODS 12). | 0,1 |
| Primeira versão funcional da PoC | A solução executa o fluxo principal proposto e permite demonstrar funcionalidade real, ainda que parcial. | 0,1 |
| Banco de dados NoSQL | Uso efetivo de NoSQL e atendimento aos requisitos previstos para o semestre (coleção única, objetos homogêneos, CRUD básico). | 0,1 |
| Programação orientada a objetos e organização do código | Uso coerente de classes/objetos, responsabilidades compreensíveis e estrutura de projeto organizada. | 0,1 |
| GitHub e versionamento | Repositório acessível, código versionado, histórico de commits e estrutura mínima organizada. | 0,1 |
| Testes automatizados | Testes relevantes, executáveis e coerentes com as funcionalidades implementadas. | 0,1 |
| Cobertura de testes ≥ 70% | Relatório ou comando reproduzível evidencia cobertura mínima de 70%. Abaixo disso, este item vale 0. | 0,1 |
| Vídeo de demonstração (2 a 3 min) | Apresenta problema, ODS, arquitetura inicial e execução da PoC dentro do tempo previsto. | 0,3 |

## Requisitos técnicos obrigatórios (toda a AEP, não só esta entrega)

- Uso efetivo de banco de dados NoSQL.
- Linguagem com suporte a POO, com aplicação efetiva do paradigma.
- Código-fonte versionado em repositório GitHub acessível.
- Testes automatizados executáveis.
- Cobertura mínima de 70% em cada entrega, com evidência reproduzível.
- Documentação técnica suficiente para compreender, instalar, executar e testar.
- PoC executável e compatível com os requisitos do semestre.

## Escopo travado do 1º semestre (seção 8 do PDF)

- Uma única coleção NoSQL.
- Objetos homogêneos, com estrutura simples.
- Operações básicas de CRUD.

Qualquer coisa além disso (múltiplas coleções, relacionamento entre coleções, documentos aninhados/subdocumentos) é **explicitamente da 2ª entrega**, não desta. Ver também as regras de escopo em `CLAUDE.md` na raiz do repositório, que traduzem isso para decisões concretas de código deste projeto (Gemini como único provider, sem LangGraph/agents, sem front-end).

## Organização mínima do repositório (seção 9 do PDF)

- `README.md`.
- Código-fonte da PoC.
- Documentação técnica.
- Testes automatizados.
- Instrução ou evidência reproduzível para gerar o relatório de cobertura.
- Identificação clara da versão da entrega (tag, release ou commit informado).
