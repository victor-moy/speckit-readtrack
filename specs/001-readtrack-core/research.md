# Phase 0 Research: ReadTrack Core

## Decisão 1: Linguagem e ambiente

- **Decision**: Python 3.11+.
- **Rationale**: amplamente disponível, biblioteca padrão cobre 100% das
  necessidades (CLI, persistência, JSON), baixa barreira de manutenção para um
  projeto pessoal solo.
- **Alternatives considered**: Go (binário único, mas overhead de setup
  desproporcional ao escopo); Node.js (exigiria dependências de terceiros até
  para SQLite, contra o Princípio I).

## Decisão 2: Interface de linha de comando

- **Decision**: `argparse` (biblioteca padrão), com subcomandos via
  `add_subparsers`.
- **Rationale**: cobre integralmente os requisitos de UX da constituição
  (`--help` automático, subcomandos no infinitivo, exit codes), sem adicionar
  dependência externa.
- **Alternatives considered**: `click`/`typer` — mais ergonômicos para CLIs
  grandes, mas introduzem dependência de terceiros não justificada pelo escopo
  atual (poucos subcomandos, sem necessidade de recursos avançados como
  autocomplete plugável).

## Decisão 3: Persistência

- **Decision**: SQLite via módulo `sqlite3` da biblioteca padrão, arquivo único
  em `~/.readtrack/readtrack.db`.
- **Rationale**: suporta índices para busca/filtro performático (SC-003),
  transações atômicas (evita corrupção em escrita concorrente acidental),
  zero-config (sem servidor), e é trivialmente exportável para JSON.
- **Alternatives considered**: arquivo JSON simples (suficiente para poucos
  livros, mas filtragem/busca em texto vira O(n) manual e não escala tão bem
  quanto um índice SQL; ainda assim, aceitável — SQLite foi preferido por
  já vir com índice e zero custo extra de dependência).

## Decisão 4: Testes

- **Decision**: `pytest` como dependência de desenvolvimento (não-runtime).
- **Rationale**: é a ferramenta de testes padrão de fato no ecossistema Python,
  exigida explicitamente pela constituição (Test-First / TDD).
- **Alternatives considered**: `unittest` (biblioteca padrão, evitaria até essa
  dependência de dev) — descartado por verbosidade e por `pytest` ser
  explicitamente mencionado como padrão na constituição do projeto.

## Decisão 5: Formato de export/import (FR-016/FR-017)

- **Decision**: JSON com uma lista de objetos, um por livro, contendo todos os
  campos da entidade `Book` (incluindo identificador, para restaurar com
  fidelidade).
- **Rationale**: JSON é legível por humanos (requisito da constituição —
  "nunca preso ao formato interno"), nativamente suportado pela biblioteca
  padrão (`json`), e suficiente para um round-trip sem perdas (SC-007).
- **Alternatives considered**: CSV — mais difícil de representar campos
  opcionais/aninhados sem ambiguidade; ficou descartado para a v1, mas pode ser
  um formato adicional em iteração futura se necessário.

## Resumo

Nenhum item da Technical Context ficou como `NEEDS CLARIFICATION`. Todas as
decisões usam exclusivamente a biblioteca padrão do Python em runtime,
satisfazendo o Princípio I (Simplicidade) e a seção de Qualidade de Código da
constituição.
