# ReadTrack

CLI pessoal para controlar os livros que você está lendo, já leu ou quer ler.
Documentado e construído com [Spec-Driven Development](https://github.com/github/spec-kit)
(GitHub Spec Kit) — veja `specs/001-readtrack-core/` para constituição, spec, plano e tasks.

## Instalação

Requer Python 3.11+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

> **Nota de ambiente**: em alguns ambientes sandboxed o processamento de
> arquivos `.pth` (usado pelo `pip install -e`) pode ser bloqueado por
> políticas de segurança. Se o comando `readtrack` não for encontrado após a
> instalação, use `PYTHONPATH=src python -m readtrack ...` como alternativa, ou
> configure `pytest` (já feito em `pyproject.toml` via `tool.pytest.ini_options.pythonpath`).

## Uso

```bash
readtrack add --title "Duna" --author "Frank Herbert"
readtrack list
readtrack list --status lido
readtrack status <ID> lendo
readtrack status <ID> lido
readtrack rate <ID> 5
readtrack note <ID> "Reler em alguns anos."
readtrack search "duna"
readtrack stats
readtrack remove <ID>
readtrack export backup.json
readtrack import backup.json
```

Todos os comandos aceitam `--json` (quando aplicável) para saída estruturada, e
retornam exit code `0` em sucesso ou `1` em erro de uso (livro não encontrado,
validação, etc.).

## Dados

Os dados ficam em um arquivo SQLite local: `~/.readtrack/readtrack.db`. Não há
rede, conta de usuário ou telemetria envolvida (ver `.specify/memory/constitution.md`).
Para mudar o local do banco (ex.: em testes), defina a variável de ambiente
`READTRACK_DB_PATH`.

## Desenvolvimento

```bash
pytest            # roda toda a suíte (unit, contract, integration)
ruff check .       # lint
ruff format .      # formatação
```

## Documentação Spec-Driven Development

Todo o processo de especificação deste projeto está em
`specs/001-readtrack-core/`:

- `spec.md` — o quê e por quê (user stories, requisitos funcionais)
- `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md` — como (plano técnico)
- `tasks.md` — quebra de tarefas executáveis, rastreadas também como
  [issues no GitHub](https://github.com/victor-moy/speckit-readtrack/issues)
- `.specify/memory/constitution.md` — princípios que guiaram todas as decisões acima
