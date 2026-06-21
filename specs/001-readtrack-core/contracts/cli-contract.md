# CLI Contract: ReadTrack Core

Interface exposta ao usuário: comando `readtrack` (entry point instalado via
`pip install -e .`), executável também como `python -m readtrack`.

Convenções globais (Princípio III da constituição):
- Saída de sucesso → stdout; erros → stderr.
- Código de saída `0` em sucesso; `1` em erro de validação/uso; `2` em erro
  inesperado.
- Toda saída suporta um modo legível por humano (default) e, quando
  `--json` é passado, saída JSON estruturada.

## `readtrack add`

```text
readtrack add --title TITLE --author AUTHOR
```

- **Sucesso**: imprime o `id` gerado, título, autor e status inicial
  (`quero ler`). Exit code `0`.
- **Erro**: `--title` ou `--author` vazios → mensagem de erro explicando o
  campo obrigatório ausente. Exit code `1`. (FR-001, FR-003)

## `readtrack list`

```text
readtrack list [--status {quero_ler|lendo|lido}] [--json]
```

- **Sucesso**: lista livros (id, título, autor, status), opcionalmente filtrada
  por `--status`. Coleção vazia → mensagem informativa, não erro. (FR-004,
  FR-011)

## `readtrack status`

```text
readtrack status BOOK_ID {quero_ler|lendo|lido}
```

- **Sucesso**: atualiza o status; imprime o novo estado e quaisquer datas
  preenchidas automaticamente (`started_at`/`finished_at`). Exit code `0`.
  (FR-005, FR-006)
- **Erro**: `BOOK_ID` inexistente → mensagem clara, exit code `1`. (FR-007)

## `readtrack rate`

```text
readtrack rate BOOK_ID RATING
```

- **Sucesso**: define a nota (1–5) de um livro com `status == lido`. Exit code
  `0`. (FR-008)
- **Erro**: `RATING` fora de `[1,5]`, `BOOK_ID` inexistente, ou livro não está
  com status `lido` → mensagem explicativa específica para cada caso, exit
  code `1`. (FR-007, FR-008)

## `readtrack note`

```text
readtrack note BOOK_ID "texto da nota"
```

- **Sucesso**: define/substitui a nota pessoal do livro, independente do
  status. Exit code `0`. (FR-009)
- **Erro**: `BOOK_ID` inexistente → exit code `1`. (FR-007)

## `readtrack search`

```text
readtrack search TERMO [--json]
```

- **Sucesso**: lista livros cujo título ou autor contenha `TERMO`
  (case-insensitive). Nenhum resultado → mensagem informativa, exit code `0`.
  (FR-010)

## `readtrack stats`

```text
readtrack stats [--json]
```

- **Sucesso**: imprime total de livros lidos, livros lidos no ano corrente, e
  nota média (ou "sem avaliações" se não houver nenhuma nota). (FR-012)

## `readtrack remove`

```text
readtrack remove BOOK_ID
```

- **Sucesso**: remove o livro da coleção. Exit code `0`. (FR-013)
- **Erro**: `BOOK_ID` inexistente → exit code `1`. (FR-007)

## `readtrack export`

```text
readtrack export ARQUIVO.json
```

- **Sucesso**: grava a coleção inteira em `ARQUIVO.json` no formato descrito em
  `data-model.md`. Exit code `0`. (FR-016)

## `readtrack import`

```text
readtrack import ARQUIVO.json
```

- **Sucesso**: restaura/mescla livros do arquivo na base local (upsert por
  `id`), sem perda de dados existentes não conflitantes. Exit code `0`.
  (FR-017)
- **Erro**: arquivo inexistente ou JSON malformado → mensagem clara, exit code
  `1`.
