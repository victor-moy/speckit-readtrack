# Data Model: ReadTrack Core

## Entity: Book

Representa um item da coleção pessoal de leitura.

| Campo | Tipo | Obrigatório | Descrição / Regras de validação |
|---|---|---|---|
| `id` | `str` (UUID curto, ex.: 8 chars hex) | Sim (gerado pelo sistema) | Identificador único, estável, exibido ao usuário em comandos que referenciam um livro específico. |
| `title` | `str` | Sim | Não pode ser vazio/whitespace (FR-003). |
| `author` | `str` | Sim | Não pode ser vazio/whitespace. |
| `status` | `ReadingStatus` (enum: `want_to_read`, `reading`, `read`) | Sim | Default `want_to_read` na criação (FR-002). Transição livre entre os três estados (sem máquina de estados restritiva — ver Edge Cases do spec). |
| `started_at` | `date` opcional | Não | Preenchido automaticamente quando status muda para `reading` (FR-006), caso ainda não definido. |
| `finished_at` | `date` opcional | Não | Preenchido automaticamente quando status muda para `read` (FR-006), caso ainda não definido. |
| `rating` | `int` opcional (1–5) | Não | Só pode ser definido quando `status == read` (FR-008); caso contrário, operação é rejeitada. |
| `notes` | `str` opcional | Não | Texto livre, editável independentemente do status (FR-009). |
| `created_at` | `datetime` | Sim (gerado pelo sistema) | Data de cadastro do livro na coleção. |

### Regras de validação (derivadas dos Functional Requirements)

- `title` e `author` não podem ser strings vazias (FR-003).
- `rating`, se definido, DEVE estar no intervalo `[1, 5]` e DEVE exigir
  `status == read` (FR-008).
- Atualizar `status` para `reading` define `started_at = hoje` apenas se ainda
  não estiver definido (idempotente em re-transições).
- Atualizar `status` para `read` define `finished_at = hoje` apenas se ainda não
  estiver definido.
- Operações que referenciam um `id` inexistente retornam erro (FR-007), nunca
  criam um registro novo implicitamente.

### State Transitions (ReadingStatus)

```text
want_to_read ⇄ reading ⇄ read
       └────────────────────┘   (transição direta também permitida)
```

Não há transições proibidas entre os três estados — qualquer transição é válida
a qualquer momento (ver Edge Cases no spec.md). O que muda são os efeitos
colaterais (preenchimento de `started_at`/`finished_at`) e as permissões
derivadas (somente `read` permite `rating`).

## Entity: ReadingStatus (enum)

| Valor interno | Rótulo exibido ao usuário (pt-BR) |
|---|---|
| `want_to_read` | quero ler |
| `reading` | lendo |
| `read` | lido |

## Estatísticas derivadas (não persistidas — calculadas em runtime)

- **Total lidos**: `COUNT(*) WHERE status = 'read'`.
- **Lidos no ano corrente**: `COUNT(*) WHERE status = 'read' AND strftime('%Y', finished_at) = strftime('%Y', 'now')`.
- **Nota média**: `AVG(rating) WHERE rating IS NOT NULL`; exibir "sem avaliações"
  quando o conjunto resultante for vazio (FR-012, Edge Cases).

## Esquema SQLite (camada `storage.py`)

```sql
CREATE TABLE IF NOT EXISTS books (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('want_to_read', 'reading', 'read')),
    started_at TEXT,
    finished_at TEXT,
    rating INTEGER CHECK (rating IS NULL OR (rating BETWEEN 1 AND 5)),
    notes TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_books_status ON books(status);
CREATE INDEX IF NOT EXISTS idx_books_title_author ON books(title, author);
```

## Formato de Export/Import (FR-016/FR-017)

Arquivo JSON com a seguinte forma (lista de objetos `Book` serializados
diretamente, preservando todos os campos da tabela acima):

```json
[
  {
    "id": "a1b2c3d4",
    "title": "Duna",
    "author": "Frank Herbert",
    "status": "read",
    "started_at": "2026-01-05",
    "finished_at": "2026-01-20",
    "rating": 5,
    "notes": "Reler em alguns anos.",
    "created_at": "2026-01-01T10:00:00"
  }
]
```

A importação (restore) substitui ou mescla por `id`: se um `id` do arquivo já
existir na base local, o registro é sobrescrito; caso contrário, é inserido.
Isso garante round-trip sem perda mesmo em restaurações repetidas (SC-007).
