# Quickstart: ReadTrack Core

Guia de validação ponta-a-ponta da feature `001-readtrack-core`. Não contém
código de implementação — apenas os passos para provar que o comportamento
descrito em `spec.md` funciona, usando os contratos em `contracts/cli-contract.md`.

## Pré-requisitos

- Python 3.11+ instalado.
- Projeto instalado em modo desenvolvimento: `pip install -e .` (a partir da
  raiz do repositório, uma vez que `pyproject.toml` exista — ver tasks.md).

## Cenário 1 — Cadastrar e listar (User Story 1)

```bash
readtrack add --title "Duna" --author "Frank Herbert"
readtrack list
```

**Resultado esperado**: o livro "Duna" aparece na listagem com status
"quero ler".

## Cenário 2 — Atualizar status de leitura (User Story 2)

```bash
readtrack status <BOOK_ID> lendo
readtrack status <BOOK_ID> lido
readtrack list
```

**Resultado esperado**: o status final é "lido"; `started_at` e `finished_at`
foram preenchidos automaticamente.

## Cenário 3 — Avaliar e anotar (User Story 3)

```bash
readtrack rate <BOOK_ID> 5
readtrack note <BOOK_ID> "Reler em alguns anos."
```

**Resultado esperado**: nota 5 e a nota pessoal aparecem ao listar/consultar o
livro. Tentar `rate` em um livro ainda "quero ler" deve falhar com mensagem
clara (exit code 1).

## Cenário 4 — Buscar, filtrar e estatísticas (User Story 4)

```bash
readtrack search "Duna"
readtrack list --status lido
readtrack stats
```

**Resultado esperado**: a busca encontra o livro por título; o filtro retorna
apenas livros "lido"; `stats` mostra total lido = 1, lido no ano corrente = 1
(assumindo execução no mesmo ano), nota média = 5.0.

## Cenário 5 — Backup e restauração (FR-016/FR-017)

```bash
readtrack export backup.json
rm -rf ~/.readtrack
readtrack import backup.json
readtrack list
```

**Resultado esperado**: após remover a base local e importar o backup, a
listagem mostra exatamente os mesmos livros, com os mesmos `id`s, status, datas,
nota e nota pessoal (SC-007).

## Execução dos testes automatizados

```bash
pytest tests/unit tests/integration tests/contract -v
```

**Resultado esperado**: todos os testes passam, cobrindo as regras de negócio
(unit), persistência/round-trip (integration) e contrato da CLI (contract).
