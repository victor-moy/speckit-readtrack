from datetime import date

from readtrack.domain import ReadingStatus, create_book, set_rating, update_status
from readtrack.stats import compute_stats


def _read_book(title: str, author: str, rating: int | None, finished_at: date) -> object:
    book = create_book(title, author)
    update_status(book, ReadingStatus.READ)
    book.finished_at = finished_at
    if rating is not None:
        set_rating(book, rating)
    return book


def test_compute_stats_with_no_books():
    result = compute_stats([])
    assert result.total_read == 0
    assert result.read_this_year == 0
    assert result.average_rating is None
    assert result.average_rating_display == "sem avaliações"


def test_compute_stats_counts_only_read_books():
    today = date(2026, 6, 21)
    books = [
        create_book("Livro A", "Autor A"),  # quero ler -> não conta
        _read_book("Livro B", "Autor B", rating=4, finished_at=today),
    ]
    result = compute_stats(books, today=today)
    assert result.total_read == 1
    assert result.read_this_year == 1


def test_compute_stats_read_this_year_filters_by_year():
    today = date(2026, 6, 21)
    last_year = date(2025, 1, 1)
    books = [
        _read_book("Livro Este Ano", "Autor", rating=5, finished_at=today),
        _read_book("Livro Ano Passado", "Autor", rating=3, finished_at=last_year),
    ]
    result = compute_stats(books, today=today)
    assert result.total_read == 2
    assert result.read_this_year == 1


def test_compute_stats_average_rating_ignores_unrated_books():
    today = date(2026, 6, 21)
    books = [
        _read_book("Com nota", "Autor", rating=4, finished_at=today),
        _read_book("Sem nota", "Autor", rating=None, finished_at=today),
    ]
    result = compute_stats(books, today=today)
    assert result.average_rating == 4.0
    assert result.average_rating_display == "4.0"


def test_compute_stats_no_ratings_shows_sem_avaliacoes():
    today = date(2026, 6, 21)
    books = [_read_book("Sem nota", "Autor", rating=None, finished_at=today)]
    result = compute_stats(books, today=today)
    assert result.average_rating is None
    assert result.average_rating_display == "sem avaliações"
