# Tasks: ReadTrack Core

**Input**: Design documents from `/specs/001-readtrack-core/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-contract.md, quickstart.md

**Tests**: Constituição do projeto exige TDD (Princípio II, NÃO NEGOCIÁVEL) —
testes são, portanto, obrigatórios e devem ser escritos antes da implementação em
cada user story.

**Organization**: Tasks agrupadas por user story (spec.md) para permitir
implementação e teste independentes de cada uma.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependências)
- **[Story]**: A qual user story a task pertence (US1–US5)
- Caminhos de arquivo exatos incluídos em cada descrição

## Path Conventions

Projeto único (CLI) conforme `plan.md`: `src/readtrack/`, `tests/` na raiz do
repositório.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialização do projeto Python

- [X] T001 Criar estrutura de diretórios `src/readtrack/`, `tests/unit/`, `tests/integration/`, `tests/contract/` conforme `plan.md`
- [X] T002 Criar `pyproject.toml` na raiz do repositório: metadados do pacote, entry point `readtrack = readtrack.cli:main`, dependências de runtime vazias, dependências de dev (`pytest`, `ruff`)
- [X] T003 [P] Configurar `ruff` (lint + format) em `pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura central que TODAS as user stories dependem

**⚠️ CRITICAL**: Nenhuma user story pode começar antes desta fase estar completa

- [X] T004 Definir enum `ReadingStatus` e dataclass `Book` (campos da entidade, sem regras de negócio ainda) em `src/readtrack/domain.py`
- [X] T005 Implementar bootstrap do SQLite (`get_db_path()`, `init_db()`, criação de tabela `books` e índices) em `src/readtrack/storage.py`, conforme esquema em `data-model.md`
- [X] T006 [P] Implementar esqueleto da CLI: parser `argparse` top-level com `add_subparsers`, registro vazio de subcomandos, em `src/readtrack/cli.py`, e ponto de entrada em `src/readtrack/__main__.py`
- [X] T007 [P] Criar fixture `pytest` de banco SQLite temporário (isolado por teste, via `tmp_path`) em `tests/conftest.py`

**Checkpoint**: Fundação pronta — implementação das user stories pode começar

---

## Phase 3: User Story 1 - Cadastrar e listar livros (Priority: P1) 🎯 MVP

**Goal**: Permitir cadastrar um livro (título + autor) e listar a coleção.

**Independent Test**: Executar `readtrack add` seguido de `readtrack list` e
confirmar que o livro cadastrado aparece na listagem com status "quero ler".

### Tests for User Story 1 ⚠️

> Escrever estes testes PRIMEIRO; garantir que falham antes de implementar.

- [X] T008 [P] [US1] Contract test para `readtrack add` (sucesso e erro de título/autor vazio) e `readtrack list` (coleção vazia e populada) em `tests/contract/test_cli_contract.py`
- [X] T009 [P] [US1] Unit test de validação de criação de `Book` (rejeita título/autor vazio, status inicial "quero ler") em `tests/unit/test_domain.py`

### Implementation for User Story 1

- [X] T010 [US1] Implementar `create_book(title, author) -> Book` com validação (FR-001, FR-002, FR-003) em `src/readtrack/domain.py` (depende de T004; faz T009 passar)
- [X] T011 [US1] Implementar `insert_book(book)` e `list_books(status=None)` em `src/readtrack/storage.py` (depende de T005)
- [X] T012 [US1] Implementar subcomandos `add` e `list` (sem `--status` ainda) em `src/readtrack/cli.py` (depende de T006, T010, T011; faz T008 passar)
- [X] T013 [US1] Adicionar formatação de saída legível e `--json` para `add`/`list` em `src/readtrack/cli.py`

**Checkpoint**: User Story 1 funcional e testável de forma independente (MVP)

---

## Phase 4: User Story 2 - Atualizar o status de leitura (Priority: P2)

**Goal**: Permitir mudar o status de um livro entre "quero ler", "lendo" e "lido",
com preenchimento automático de datas.

**Independent Test**: Cadastrar um livro, alterar seu status duas vezes e
confirmar que `started_at`/`finished_at` foram preenchidos corretamente.

### Tests for User Story 2 ⚠️

- [X] T014 [P] [US2] Contract test para `readtrack status` (transições válidas + erro de id inexistente) em `tests/contract/test_cli_contract.py`
- [X] T015 [P] [US2] Unit test dos efeitos colaterais de transição de status (preenchimento de datas, idempotência) em `tests/unit/test_domain.py`

### Implementation for User Story 2

- [X] T016 [US2] Implementar `update_status(book, new_status)` com preenchimento automático de `started_at`/`finished_at` (FR-005, FR-006) em `src/readtrack/domain.py` (depende de T010; faz T015 passar)
- [X] T017 [US2] Implementar `get_book(book_id)` e `update_book(book)` em `src/readtrack/storage.py` (depende de T011)
- [X] T018 [US2] Implementar subcomando `status` com erro claro para id inexistente (FR-007) em `src/readtrack/cli.py` (depende de T012, T016, T017; faz T014 passar)

**Checkpoint**: User Stories 1 e 2 funcionam de forma independente

---

## Phase 5: User Story 3 - Avaliar e anotar livros lidos (Priority: P3)

**Goal**: Permitir atribuir nota (1-5, somente se "lido") e nota pessoal a um
livro.

**Independent Test**: Marcar um livro como "lido", atribuir nota e nota pessoal,
e confirmar nos detalhes; confirmar que avaliar um livro "quero ler"/"lendo" é
rejeitado.

### Tests for User Story 3 ⚠️

- [X] T019 [P] [US3] Contract test para `readtrack rate` (sucesso, nota fora de 1-5, e rejeição quando status != "lido") e `readtrack note` em `tests/contract/test_cli_contract.py`
- [X] T020 [P] [US3] Unit test das regras de avaliação (`rating` exige status "lido", intervalo 1-5) em `tests/unit/test_domain.py`

### Implementation for User Story 3

- [X] T021 [US3] Implementar `set_rating(book, rating)` e `set_notes(book, notes)` com validação (FR-008, FR-009) em `src/readtrack/domain.py` (depende de T016; faz T020 passar)
- [X] T022 [US3] Estender `update_book()` para persistir `rating`/`notes` em `src/readtrack/storage.py` (depende de T017)
- [X] T023 [US3] Implementar subcomandos `rate` e `note` em `src/readtrack/cli.py` (depende de T018, T021, T022; faz T019 passar)

**Checkpoint**: User Stories 1, 2 e 3 funcionam de forma independente

---

## Phase 6: User Story 4 - Buscar, filtrar e ver estatísticas (Priority: P4)

**Goal**: Permitir buscar por título/autor, filtrar por status, e ver
estatísticas de leitura (total lido, lido no ano, nota média).

**Independent Test**: Popular a coleção com livros em status/notas variados e
validar `search`, `list --status` e `stats` isoladamente.

### Tests for User Story 4 ⚠️

- [X] T024 [P] [US4] Contract test para `readtrack search`, `readtrack list --status` e `readtrack stats` (incluindo caso "sem avaliações") em `tests/contract/test_cli_contract.py`
- [X] T025 [P] [US4] Unit test do cálculo de estatísticas (total lido, lido no ano corrente, média, divisão por zero) em `tests/unit/test_stats.py`

### Implementation for User Story 4

- [X] T026 [US4] Implementar `search_books(term)` e suporte a filtro por `status` em `list_books()` (FR-010, FR-011) em `src/readtrack/storage.py` (depende de T011)
- [X] T027 [US4] Implementar `compute_stats(books)` (total lido, lido no ano, média ou "sem avaliações") (FR-012) em `src/readtrack/stats.py` (depende de T011; faz T025 passar)
- [X] T028 [US4] Implementar subcomando `search`, flag `--status` em `list`, e subcomando `stats` em `src/readtrack/cli.py` (depende de T012, T026, T027; faz T024 passar)

**Checkpoint**: Todas as 4 user stories centrais funcionam de forma independente

---

## Phase 7: User Story 5 - Backup e restauração de dados (Priority: P5)

**Goal**: Permitir exportar a coleção inteira para JSON e restaurá-la a partir
desse arquivo, sem perda de dados.

**Independent Test**: Popular a coleção, exportar, apagar a base local,
importar o arquivo de volta, e confirmar que a coleção é idêntica.

### Tests for User Story 5 ⚠️

- [X] T029 [P] [US5] Contract test para `readtrack export` e `readtrack import` (round-trip e erro de arquivo inexistente/malformado) em `tests/contract/test_cli_contract.py`
- [X] T030 [P] [US5] Integration test de round-trip export→import preservando todos os campos em `tests/integration/test_storage_roundtrip.py`

### Implementation for User Story 5

- [X] T031 [US5] Implementar `export_books(path)` (serialização JSON de todos os livros) (FR-016) em `src/readtrack/storage.py` (depende de T011; faz parte de T030 passar)
- [X] T032 [US5] Implementar `import_books(path)` (upsert por `id`, validação de JSON) (FR-017) em `src/readtrack/storage.py` (depende de T031; faz T030 passar)
- [X] T033 [US5] Implementar subcomandos `export` e `import` com tratamento de erro de arquivo ausente/malformado em `src/readtrack/cli.py` (depende de T012, T031, T032; faz T029 passar)

**Checkpoint**: Todas as 5 user stories funcionam de forma independente

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Validação final e qualidade transversal

- [X] T034 [P] Adicionar `README.md` na raiz com instruções de instalação (`pip install -e .`) e uso de todos os subcomandos
- [X] T035 Revisar mensagens de erro de todos os subcomandos para consistência (Princípio III da constituição)
- [X] T036 [P] Medir tempo de resposta de `list`/`search`/`stats` com 10.000 livros sintéticos e confirmar SC-003 (<200ms)
- [X] T037 Executar manualmente todos os cenários de `quickstart.md` e confirmar os resultados esperados
- [X] T038 Rodar `ruff check` e `ruff format --check` em todo o projeto e corrigir achados

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências — pode iniciar imediatamente
- **Foundational (Phase 2)**: depende da conclusão do Setup — BLOQUEIA todas as user stories
- **User Stories (Phase 3-7)**: todas dependem da conclusão da Foundational
  - Podem ser feitas em paralelo (se houver mais de um desenvolvedor) ou em ordem de prioridade (P1→P2→P3→P4→P5)
- **Polish (Phase 8)**: depende de todas as user stories desejadas estarem completas

### User Story Dependencies

- **US1 (P1)**: nenhuma dependência de outra story
- **US2 (P2)**: reutiliza `create_book`/storage de US1, mas é testável de forma independente
- **US3 (P3)**: reutiliza `update_status` de US2 (precisa de status "lido"), testável de forma independente
- **US4 (P4)**: reutiliza `list_books`/storage de US1, testável de forma independente
- **US5 (P5)**: reutiliza `list_books`/storage de US1, testável de forma independente

### Within Each User Story

- Testes (contract/unit/integration) DEVEM ser escritos e falhar antes da implementação
- Domínio (`domain.py`/`stats.py`) antes de storage; storage antes de CLI
- Story completa antes de avançar para a próxima prioridade (se sequencial)

### Parallel Opportunities

- T003 (Setup) pode rodar em paralelo com T002
- T006 e T007 (Foundational) podem rodar em paralelo entre si (após T004/T005)
- Testes marcados [P] dentro de cada user story podem rodar em paralelo
- Após a Foundational, US1-US5 podem ser desenvolvidas em paralelo por pessoas diferentes (cada uma toca arquivos diferentes na maior parte, exceto `cli.py`/`storage.py`, que devem ser mesclados com cuidado)

---

## Parallel Example: User Story 1

```bash
# Lançar os testes da User Story 1 juntos:
Task: "Contract test para readtrack add/list em tests/contract/test_cli_contract.py"
Task: "Unit test de validação de Book em tests/unit/test_domain.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 apenas)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (CRÍTICO — bloqueia todas as stories)
3. Completar Phase 3: User Story 1
4. **PARAR e VALIDAR**: testar User Story 1 de forma independente
5. Demonstrar se estiver pronto

### Incremental Delivery

1. Setup + Foundational → fundação pronta
2. US1 → testar independentemente → demo (MVP!)
3. US2 → testar independentemente → demo
4. US3 → testar independentemente → demo
5. US4 → testar independentemente → demo
6. US5 → testar independentemente → demo
7. Phase 8: Polish

---

## Notes

- [P] = arquivos diferentes, sem dependências entre si
- [Story] mapeia a task para a user story correspondente (rastreabilidade)
- Cada user story deve ser completável e testável de forma independente
- Verificar que os testes falham antes de implementar (Red-Green-Refactor)
- Fazer commit após cada task ou grupo lógico de tasks
- Parar em qualquer checkpoint para validar a story isoladamente
