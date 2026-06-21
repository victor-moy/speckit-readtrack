"""Interface de linha de comando do ReadTrack (Princípio III: UX consistente)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from readtrack import storage
from readtrack.domain import (
    Book,
    BookNotFoundError,
    ReadingStatus,
    ValidationError,
    create_book,
    set_notes,
    set_rating,
    update_status,
)
from readtrack.stats import compute_stats

EXIT_OK = 0
EXIT_USAGE_ERROR = 1
EXIT_UNEXPECTED_ERROR = 2


def _book_to_dict(book: Book) -> dict:
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "status": book.status.value,
        "status_label": book.status.label,
        "started_at": book.started_at.isoformat() if book.started_at else None,
        "finished_at": book.finished_at.isoformat() if book.finished_at else None,
        "rating": book.rating,
        "notes": book.notes,
    }


def _print_book_line(book: Book) -> None:
    parts = [f"[{book.id}] {book.title} — {book.author} ({book.status.label})"]
    if book.rating is not None:
        parts.append(f"nota: {book.rating}/5")
    print(" | ".join(parts))


def _print_books(books: list[Book], as_json: bool) -> None:
    if as_json:
        print(json.dumps([_book_to_dict(b) for b in books], ensure_ascii=False, indent=2))
        return
    if not books:
        print("Nenhum livro encontrado.")
        return
    for book in books:
        _print_book_line(book)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="readtrack",
        description="Controle pessoal dos livros que você está lendo, quer ler ou já leu.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="Cadastrar um novo livro")
    add_p.add_argument("--title", required=True, help="Título do livro")
    add_p.add_argument("--author", required=True, help="Autor do livro")
    add_p.add_argument("--json", action="store_true", help="Saída em JSON")

    list_p = sub.add_parser("list", help="Listar livros da coleção")
    list_p.add_argument(
        "--status",
        choices=["quero_ler", "lendo", "lido"],
        help="Filtrar por status",
    )
    list_p.add_argument("--json", action="store_true", help="Saída em JSON")

    status_p = sub.add_parser("status", help="Atualizar o status de leitura de um livro")
    status_p.add_argument("book_id")
    status_p.add_argument("new_status", choices=["quero_ler", "lendo", "lido"])
    status_p.add_argument("--json", action="store_true", help="Saída em JSON")

    rate_p = sub.add_parser("rate", help="Avaliar um livro lido (nota de 1 a 5)")
    rate_p.add_argument("book_id")
    rate_p.add_argument("rating", type=int)

    note_p = sub.add_parser("note", help="Adicionar/editar a nota pessoal de um livro")
    note_p.add_argument("book_id")
    note_p.add_argument("text")

    search_p = sub.add_parser("search", help="Buscar livros por título ou autor")
    search_p.add_argument("term")
    search_p.add_argument("--json", action="store_true", help="Saída em JSON")

    sub.add_parser("stats", help="Ver estatísticas de leitura").add_argument(
        "--json", action="store_true", help="Saída em JSON"
    )

    remove_p = sub.add_parser("remove", help="Remover um livro da coleção")
    remove_p.add_argument("book_id")

    export_p = sub.add_parser("export", help="Exportar a coleção para um arquivo JSON")
    export_p.add_argument("path")

    import_p = sub.add_parser("import", help="Importar/restaurar a coleção de um arquivo JSON")
    import_p.add_argument("path")

    return parser


def _connect():
    return storage.init_db(storage.get_db_path())


def _cmd_add(args: argparse.Namespace) -> int:
    try:
        book = create_book(args.title, args.author)
    except ValidationError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    conn = _connect()
    storage.insert_book(conn, book)
    if args.json:
        print(json.dumps(_book_to_dict(book), ensure_ascii=False, indent=2))
    else:
        print(f"Livro cadastrado: [{book.id}] {book.title} — {book.author} ({book.status.label})")
    return EXIT_OK


def _cmd_list(args: argparse.Namespace) -> int:
    status = ReadingStatus.parse(args.status) if args.status else None
    conn = _connect()
    books = storage.list_books(conn, status=status)
    _print_books(books, args.json)
    return EXIT_OK


def _cmd_status(args: argparse.Namespace) -> int:
    conn = _connect()
    try:
        book = storage.get_book(conn, args.book_id)
    except BookNotFoundError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    new_status = ReadingStatus.parse(args.new_status)
    update_status(book, new_status)
    storage.update_book(conn, book)
    if args.json:
        print(json.dumps(_book_to_dict(book), ensure_ascii=False, indent=2))
    else:
        print(f"Status atualizado: [{book.id}] agora está '{book.status.label}'.")
    return EXIT_OK


def _cmd_rate(args: argparse.Namespace) -> int:
    conn = _connect()
    try:
        book = storage.get_book(conn, args.book_id)
    except BookNotFoundError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    try:
        set_rating(book, args.rating)
    except ValidationError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    storage.update_book(conn, book)
    print(f"Nota registrada: [{book.id}] {book.rating}/5.")
    return EXIT_OK


def _cmd_note(args: argparse.Namespace) -> int:
    conn = _connect()
    try:
        book = storage.get_book(conn, args.book_id)
    except BookNotFoundError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    set_notes(book, args.text)
    storage.update_book(conn, book)
    print(f"Nota pessoal atualizada para [{book.id}].")
    return EXIT_OK


def _cmd_search(args: argparse.Namespace) -> int:
    conn = _connect()
    books = storage.search_books(conn, args.term)
    _print_books(books, args.json)
    return EXIT_OK


def _cmd_stats(args: argparse.Namespace) -> int:
    conn = _connect()
    books = storage.list_books(conn)
    result = compute_stats(books)
    if args.json:
        print(
            json.dumps(
                {
                    "total_read": result.total_read,
                    "read_this_year": result.read_this_year,
                    "average_rating": result.average_rating,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"Livros lidos: {result.total_read}")
        print(f"Lidos neste ano: {result.read_this_year}")
        print(f"Nota média: {result.average_rating_display}")
    return EXIT_OK


def _cmd_remove(args: argparse.Namespace) -> int:
    conn = _connect()
    try:
        storage.delete_book(conn, args.book_id)
    except BookNotFoundError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    print(f"Livro [{args.book_id}] removido.")
    return EXIT_OK


def _cmd_export(args: argparse.Namespace) -> int:
    conn = _connect()
    count = storage.export_books(conn, Path(args.path))
    print(f"{count} livro(s) exportado(s) para {args.path}.")
    return EXIT_OK


def _cmd_import(args: argparse.Namespace) -> int:
    conn = _connect()
    try:
        count = storage.import_books(conn, Path(args.path))
    except (FileNotFoundError, ValueError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    print(f"{count} livro(s) importado(s) de {args.path}.")
    return EXIT_OK


_HANDLERS = {
    "add": _cmd_add,
    "list": _cmd_list,
    "status": _cmd_status,
    "rate": _cmd_rate,
    "note": _cmd_note,
    "search": _cmd_search,
    "stats": _cmd_stats,
    "remove": _cmd_remove,
    "export": _cmd_export,
    "import": _cmd_import,
}


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    handler = _HANDLERS[args.command]
    try:
        return handler(args)
    except Exception as exc:  # pragma: no cover - rede de segurança para erros inesperados
        print(f"Erro inesperado: {exc}", file=sys.stderr)
        return EXIT_UNEXPECTED_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
