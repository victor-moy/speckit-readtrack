"""Camada de persistência: SQLite local (sem dependências de terceiros)."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import date, datetime
from pathlib import Path

from readtrack.domain import Book, BookNotFoundError, ReadingStatus

SCHEMA = """
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
"""


def get_db_path() -> Path:
    override = os.environ.get("READTRACK_DB_PATH")
    if override:
        return Path(override)
    return Path.home() / ".readtrack" / "readtrack.db"


def init_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def _row_to_book(row: sqlite3.Row) -> Book:
    return Book(
        id=row["id"],
        title=row["title"],
        author=row["author"],
        status=ReadingStatus(row["status"]),
        started_at=date.fromisoformat(row["started_at"]) if row["started_at"] else None,
        finished_at=date.fromisoformat(row["finished_at"]) if row["finished_at"] else None,
        rating=row["rating"],
        notes=row["notes"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def _book_to_row(book: Book) -> dict:
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "status": book.status.value,
        "started_at": book.started_at.isoformat() if book.started_at else None,
        "finished_at": book.finished_at.isoformat() if book.finished_at else None,
        "rating": book.rating,
        "notes": book.notes,
        "created_at": book.created_at.isoformat(),
    }


def insert_book(conn: sqlite3.Connection, book: Book) -> Book:
    row = _book_to_row(book)
    conn.execute(
        """
        INSERT INTO books (id, title, author, status, started_at, finished_at,
                            rating, notes, created_at)
        VALUES (:id, :title, :author, :status, :started_at, :finished_at,
                :rating, :notes, :created_at)
        """,
        row,
    )
    conn.commit()
    return book


def get_book(conn: sqlite3.Connection, book_id: str) -> Book:
    row = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if row is None:
        raise BookNotFoundError(f"Nenhum livro encontrado com id '{book_id}'.")
    return _row_to_book(row)


def update_book(conn: sqlite3.Connection, book: Book) -> Book:
    row = _book_to_row(book)
    cursor = conn.execute(
        """
        UPDATE books
        SET title = :title, author = :author, status = :status,
            started_at = :started_at, finished_at = :finished_at,
            rating = :rating, notes = :notes
        WHERE id = :id
        """,
        row,
    )
    if cursor.rowcount == 0:
        raise BookNotFoundError(f"Nenhum livro encontrado com id '{book.id}'.")
    conn.commit()
    return book


def delete_book(conn: sqlite3.Connection, book_id: str) -> None:
    cursor = conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    if cursor.rowcount == 0:
        raise BookNotFoundError(f"Nenhum livro encontrado com id '{book_id}'.")
    conn.commit()


def list_books(conn: sqlite3.Connection, status: ReadingStatus | None = None) -> list[Book]:
    if status is None:
        rows = conn.execute("SELECT * FROM books ORDER BY created_at ASC").fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM books WHERE status = ? ORDER BY created_at ASC",
            (status.value,),
        ).fetchall()
    return [_row_to_book(row) for row in rows]


def search_books(conn: sqlite3.Connection, term: str) -> list[Book]:
    like = f"%{term.lower()}%"
    rows = conn.execute(
        """
        SELECT * FROM books
        WHERE lower(title) LIKE ? OR lower(author) LIKE ?
        ORDER BY created_at ASC
        """,
        (like, like),
    ).fetchall()
    return [_row_to_book(row) for row in rows]


def export_books(conn: sqlite3.Connection, path: Path) -> int:
    """Exporta toda a coleção para um arquivo JSON legível (FR-016)."""
    books = list_books(conn)
    payload = [_book_to_row(book) for book in books]
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(payload)


def import_books(conn: sqlite3.Connection, path: Path) -> int:
    """Restaura livros de um arquivo exportado, fazendo upsert por id (FR-017)."""
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de importação não encontrado: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Arquivo de importação malformado: {exc}") from exc

    count = 0
    for entry in payload:
        conn.execute(
            """
            INSERT INTO books (id, title, author, status, started_at, finished_at,
                                rating, notes, created_at)
            VALUES (:id, :title, :author, :status, :started_at, :finished_at,
                    :rating, :notes, :created_at)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                author = excluded.author,
                status = excluded.status,
                started_at = excluded.started_at,
                finished_at = excluded.finished_at,
                rating = excluded.rating,
                notes = excluded.notes,
                created_at = excluded.created_at
            """,
            entry,
        )
        count += 1
    conn.commit()
    return count
