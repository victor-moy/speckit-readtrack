"""Cálculo de estatísticas de leitura a partir de uma coleção de Book (FR-012)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from readtrack.domain import Book, ReadingStatus


@dataclass
class ReadingStats:
    total_read: int
    read_this_year: int
    average_rating: float | None

    @property
    def average_rating_display(self) -> str:
        if self.average_rating is None:
            return "sem avaliações"
        return f"{self.average_rating:.1f}"


def compute_stats(books: list[Book], *, today: date | None = None) -> ReadingStats:
    today = today or date.today()
    read_books = [book for book in books if book.status == ReadingStatus.READ]
    read_this_year = [
        book
        for book in read_books
        if book.finished_at is not None and book.finished_at.year == today.year
    ]
    ratings = [book.rating for book in read_books if book.rating is not None]
    average_rating = (sum(ratings) / len(ratings)) if ratings else None
    return ReadingStats(
        total_read=len(read_books),
        read_this_year=len(read_this_year),
        average_rating=average_rating,
    )
