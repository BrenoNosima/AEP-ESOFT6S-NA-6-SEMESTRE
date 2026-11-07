---
name: aep-rubric
description: >-
  Rubrica oficial de avaliação da AEP de Engenharia de Software (6S),
  1ª e 2ª entregas, transcrita de AEP_ESoft_6S.pdf. Carregar ao auditar o
  projeto contra os critérios de correção ou ao decidir se algo pertence
  ao escopo da entrega atual (2ª).
---

# Rubrica — 2ª Entrega da AEP (peso total: 1,0 ponto) — ENTREGA ATUAL

| Critério | Evidência esperada | Pontos |
|---|---|---|
| PoC funcional e evolução | Fluxos principais executam corretamente e há evolução verificável em relação à 1ª entrega. | 0,1 |
| Banco de dados NoSQL | Modelagem e uso do banco atendem integralmente aos requisitos do semestre (múltiplas coleções, relacionamento, objetos complexos) e às necessidades da PoC. | 0,1 |
| POO e qualidade do código | Estrutura coerente, responsabilidades bem definidas, legibilidade e ausência de duplicações ou acoplamentos desnecessários relevantes. | 0,1 |
| Metodologia de trabalho utilizada | Quadro de tarefas. | 0,1 |
| Testes automatizados | Conjunto de testes pertinente, executável e cobrindo comportamentos relevantes da solução. | 0,1 |
| Cobertura de testes ≥ 70% | Relatório ou comando reproduzível evidencia cobertura mínima de 70%. Abaixo disso, este item vale 0. | 0,1 |
| Documentação técnica | README e documentação permitem compreender, instalar, executar e testar a PoC, incluindo tecnologias e estrutura do banco. | 0,1 |
| GitHub e versionamento | Repositório organizado, histórico compatível com a evolução do trabalho e versão final claramente identificável. | 0,1 |
| Vídeo de demonstração (3 a 5 min) | Apresenta evolução, arquitetura final, execução da PoC, tecnologias, testes e principais resultados, dentro do tempo previsto. | 0,2 |

**Entregáveis:** código-fonte atualizado no GitHub; documentação técnica completa; testes executáveis com cobertura ≥ 70%; vídeo de 3 a 5 minutos.

**O vídeo deve apresentar:** a evolução da solução; o projeto final; a demonstração da PoC; as tecnologias utilizadas; os testes automatizados e a cobertura obtida; os principais resultados alcançados.

## Requisitos de banco do 2º semestre (seção 8 do PDF)

- Múltiplas coleções.
- Relacionamento entre coleções.
- Pelo menos uma coleção contendo objetos complexos, como documentos aninhados ou listas de subdocumentos.

Exemplo do PDF: `{ "nome": "João", "email": "joao@email.com", "enderecos": [ { "rua": "Rua A", "cidade": "Maringá", "estado": "PR" } ] }`.

No EcoMentor isso é atendido por `users` (com `addresses` aninhados) e `consultations` (com `user_id` e `location`). Ver `CLAUDE.md` para o que entra e o que continua fora.

## Requisitos técnicos obrigatórios (toda a AEP)

- Uso efetivo de banco de dados NoSQL.
- Linguagem com suporte a POO, com aplicação efetiva do paradigma.
- Código-fonte versionado em repositório GitHub acessível.
- Testes automatizados executáveis.
- Cobertura mínima de 70% em cada entrega, com evidência reproduzível.
- Documentação técnica suficiente para compreender, instalar, executar e testar.
- PoC executável e compatível com os requisitos do semestre.

## Organização mínima do repositório (seção 9 do PDF)

- `README.md`.
- Código-fonte da PoC.
- Documentação técnica.
- Testes automatizados.
- Instrução ou evidência reproduzível para gerar o relatório de cobertura.
- Identificação clara da versão de cada entrega (tag, release ou commit informado): `entrega-1` (feita, `2f5d256`) e `entrega-2`.

---

# Referência histórica — 1ª Entrega (concluída, tag `entrega-1`)

| Critério | Pontos |
|---|---|
| Problema e alinhamento ao ODS | 0,1 |
| Primeira versão funcional da PoC | 0,1 |
| Banco de dados NoSQL (coleção única, objetos homogêneos, CRUD) | 0,1 |
| POO e organização do código | 0,1 |
| GitHub e versionamento | 0,1 |
| Testes automatizados | 0,1 |
| Cobertura de testes ≥ 70% | 0,1 |
| Vídeo de demonstração (2 a 3 min) | 0,3 |
