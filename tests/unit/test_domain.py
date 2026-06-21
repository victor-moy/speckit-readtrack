from datetime import date

import pytest

from readtrack.domain import (
    ReadingStatus,
    ValidationError,
    create_book,
    set_notes,
    set_rating,
    update_status,
)


def test_create_book_has_default_status_want_to_read():
    book = create_book("Duna", "Frank Herbert")
    assert book.status == ReadingStatus.WANT_TO_READ
    assert book.title == "Duna"
    assert book.author == "Frank Herbert"
    assert book.id


def test_create_book_rejects_empty_title():
    with pytest.raises(ValidationError):
        create_book("   ", "Frank Herbert")


def test_create_book_rejects_empty_author():
    with pytest.raises(ValidationError):
        create_book("Duna", "")


def test_update_status_to_reading_sets_started_at():
    book = create_book("Duna", "Frank Herbert")
    update_status(book, ReadingStatus.READING)
    assert book.status == ReadingStatus.READING
    assert book.started_at == date.today()
    assert book.finished_at is None


def test_update_status_to_read_sets_finished_at():
    book = create_book("Duna", "Frank Herbert")
    update_status(book, ReadingStatus.READ)
    assert book.status == ReadingStatus.READ
    assert book.finished_at == date.today()


def test_update_status_does_not_overwrite_existing_started_at():
    book = create_book("Duna", "Frank Herbert")
    update_status(book, ReadingStatus.READING)
    original_started_at = book.started_at
    update_status(book, ReadingStatus.READING)
    assert book.started_at == original_started_at


def test_set_rating_requires_status_read():
    book = create_book("Duna", "Frank Herbert")
    with pytest.raises(ValidationError):
        set_rating(book, 5)


def test_set_rating_accepts_value_between_1_and_5():
    book = create_book("Duna", "Frank Herbert")
    update_status(book, ReadingStatus.READ)
    set_rating(book, 5)
    assert book.rating == 5


@pytest.mark.parametrize("invalid_rating", [0, 6, -1])
def test_set_rating_rejects_out_of_range(invalid_rating):
    book = create_book("Duna", "Frank Herbert")
    update_status(book, ReadingStatus.READ)
    with pytest.raises(ValidationError):
        set_rating(book, invalid_rating)


def test_set_notes_allowed_regardless_of_status():
    book = create_book("Duna", "Frank Herbert")
    set_notes(book, "Reler em alguns anos.")
    assert book.notes == "Reler em alguns anos."


def test_reading_status_parse_accepts_label_and_value():
    assert ReadingStatus.parse("quero_ler") == ReadingStatus.WANT_TO_READ
    assert ReadingStatus.parse("lendo") == ReadingStatus.READING
    assert ReadingStatus.parse("lido") == ReadingStatus.READ
    assert ReadingStatus.parse("want_to_read") == ReadingStatus.WANT_TO_READ


def test_reading_status_parse_rejects_unknown_value():
    with pytest.raises(ValidationError):
        ReadingStatus.parse("desconhecido")
