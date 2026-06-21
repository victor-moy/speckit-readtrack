"""Testes de integração: persistência real em SQLite e round-trip de export/import."""

from readtrack import storage
from readtrack.domain import ReadingStatus, create_book, set_notes, set_rating, update_status


def test_insert_and_list_persists_across_connections(db_path):
    conn = storage.init_db(db_path)
    book = create_book("Duna", "Frank Herbert")
    storage.insert_book(conn, book)
    conn.close()

    reopened = storage.init_db(db_path)
    books = storage.list_books(reopened)
    assert len(books) == 1
    assert books[0].title == "Duna"


def test_export_import_roundtrip_preserves_all_fields(conn, tmp_path):
    book = create_book("Duna", "Frank Herbert")
    update_status(book, ReadingStatus.READ)
    set_rating(book, 5)
    set_notes(book, "Reler em alguns anos.")
    storage.insert_book(conn, book)

    backup_path = tmp_path / "backup.json"
    exported_count = storage.export_books(conn, backup_path)
    assert exported_count == 1

    # Simula perda da base local e restauração a partir do backup.
    for existing in storage.list_books(conn):
        storage.delete_book(conn, existing.id)
    assert storage.list_books(conn) == []

    imported_count = storage.import_books(conn, backup_path)
    assert imported_count == 1

    restored = storage.get_book(conn, book.id)
    assert restored.title == book.title
    assert restored.author == book.author
    assert restored.status == book.status
    assert restored.started_at == book.started_at
    assert restored.finished_at == book.finished_at
    assert restored.rating == book.rating
    assert restored.notes == book.notes


def test_import_upserts_existing_book_by_id(conn, tmp_path):
    book = create_book("Duna", "Frank Herbert")
    storage.insert_book(conn, book)
    backup_path = tmp_path / "backup.json"
    storage.export_books(conn, backup_path)

    # Altera o livro localmente após o backup ter sido feito.
    book.title = "Duna (edição alterada)"
    storage.update_book(conn, book)

    storage.import_books(conn, backup_path)

    restored = storage.get_book(conn, book.id)
    assert restored.title == "Duna"  # restaurado para o valor do backup
