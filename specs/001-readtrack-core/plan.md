# Implementation Plan: ReadTrack Core

**Branch**: `001-readtrack-core` | **Date**: 2026-06-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-readtrack-core/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Construir o ReadTrack como uma CLI Python single-user para cadastrar livros,
acompanhar o status de leitura (quero ler / lendo / lido), avaliar e anotar
livros lidos, buscar/filtrar a coleção, ver estatísticas e fazer backup/restore
via export/import em JSON. Abordagem técnica: SQLite local (via `sqlite3` da
biblioteca padrão) para persistência, `argparse` (biblioteca padrão) para a
interface de linha de comando, e `pytest` para testes — sem dependências de
terceiros em runtime, em conformidade com o Princípio I (Simplicidade/CLI-First)
e a seção de Qualidade de Código da constituição (toda dependência externa deve
ser justificada; aqui, nenhuma é necessária).

## Technical Context

**Language/Version**: Python 3.11+ (ambiente de desenvolvimento usa Python 3.14)

**Primary Dependencies**: Nenhuma dependência de terceiros em runtime — apenas
biblioteca padrão (`sqlite3`, `argparse`, `dataclasses`, `json`, `datetime`).
Dependências de desenvolvimento (não-runtime): `pytest` (testes), `ruff`
(lint + format).

**Storage**: SQLite — arquivo único em `~/.readtrack/readtrack.db` (criado
automaticamente no primeiro uso). Escolhido por ser embutido na biblioteca
padrão do Python, suportar consultas indexadas (busca/filtro) sem servidor, e
atender ao requisito de persistência local sem rede (FR-014, FR-015).

**Testing**: `pytest`, com testes de unidade para a camada de domínio
(`tests/unit/`) e testes de contrato para o comportamento da CLI ponta-a-ponta
(`tests/contract/`), seguindo TDD conforme Princípio II da constituição.

**Target Platform**: Linux/macOS/Windows com Python 3.11+ instalado (qualquer
terminal compatível com stdin/stdout/stderr).

**Project Type**: CLI (projeto único — Option 1 da estrutura padrão).

**Performance Goals**: Qualquer comando deve responder perceptivelmente de forma
instantânea (Princípio V da constituição: <200ms) para coleções de até 10.000
livros (SC-003).

**Constraints**: Totalmente offline; sem autenticação; sem telemetria; arquivo de
dados deve sobreviver a encerramento/reabertura do processo (SC-006); export/
import devem ser round-trip sem perda de dados (SC-007).

**Scale/Scope**: Uso pessoal, single-user, single-machine. Escopo desta feature:
cadastro, status, avaliação/notas, busca/filtro, estatísticas, export/import.
Fora de escopo: múltiplos usuários, sincronização entre dispositivos, integração
com catálogos externos (ISBN/APIs de livros), interface gráfica.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Avaliação | Conformidade |
|---|---|---|
| I. Simplicidade em Primeiro Lugar (CLI-First) | CLI pura com `argparse`, sem servidor/GUI/DI framework; nenhuma dependência de terceiros em runtime. | ✅ PASS |
| II. Test-First (TDD) | Plano usa `pytest`; tasks (fase seguinte) devem ordenar testes antes da implementação de cada user story. | ✅ PASS (a ser verificado em `/speckit-tasks`) |
| III. Consistência de Experiência na CLI | Subcomandos no infinitivo (`add`, `list`, `status`, `rate`, `note`, `search`, `stats`, `remove`, `export`, `import`); `--help` nativo do `argparse`; códigos de saída 0/≠0. | ✅ PASS |
| IV. Dados Locais e Privacidade | SQLite local em `~/.readtrack/`; nenhuma chamada de rede; export/import em JSON cobrem a exigência de não aprisionar o usuário ao formato interno (FR-016/FR-017). | ✅ PASS |
| V. Performance Instantânea | SQLite com índices em `title`/`author`/`status` garante consultas sub-milissegundo até 10k linhas; sem otimização prematura além disso. | ✅ PASS |

Nenhuma violação identificada — **Complexity Tracking não se aplica** (seção
deixada vazia abaixo).

## Project Structure

### Documentation (this feature)

```text
specs/001-readtrack-core/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── cli-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/
└── readtrack/
    ├── __init__.py
    ├── __main__.py        # entry point: `python -m readtrack`
    ├── cli.py              # argparse setup + subcommand dispatch
    ├── domain.py           # Book, ReadingStatus, regras de negócio puras
    ├── storage.py           # camada SQLite (CRUD, schema, migrations simples)
    └── stats.py             # cálculo de estatísticas de leitura

tests/
├── contract/
│   └── test_cli_contract.py   # invoca a CLI ponta-a-ponta e valida stdout/exit code
├── integration/
│   └── test_storage_roundtrip.py  # persistência real em SQLite temporário + export/import
└── unit/
    ├── test_domain.py
    └── test_stats.py
```

**Structure Decision**: Option 1 (projeto único). Não há frontend/backend
separados nem múltiplas plataformas — é uma única CLI Python instalável via
`pip install -e .` com um entry point `readtrack`. A separação `domain.py` /
`storage.py` / `cli.py` mantém a lógica de negócio testável isoladamente da
camada de I/O (SQLite) e da camada de apresentação (argparse), conforme a seção
"Qualidade de Código" da constituição.

## Complexity Tracking

> Nenhuma violação da constituição foi identificada nesta fase — tabela
> intencionalmente vazia.
