"""Camada de domínio: entidades e regras de negócio puras (sem I/O)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum


class ReadingStatus(StrEnum):
    WANT_TO_READ = "want_to_read"
    READING = "reading"
    READ = "read"

    @property
    def label(self) -> str:
        return _STATUS_LABELS[self]

    @classmethod
    def parse(cls, value: str) -> ReadingStatus:
        normalized = (value or "").strip().lower().replace(" ", "_")
        by_value = {status.value: status for status in cls}
        by_label = {status.label.replace(" ", "_"): status for status in cls}
        if normalized in by_value:
            return by_value[normalized]
        if normalized in by_label:
            return by_label[normalized]
        raise ValidationError(
            f"Status inválido: {value!r}. Use um de: {', '.join(status.label for status in cls)}."
        )


_STATUS_LABELS = {
    ReadingStatus.WANT_TO_READ: "quero ler",
    ReadingStatus.READING: "lendo",
    ReadingStatus.READ: "lido",
}


class ValidationError(ValueError):
    """Erro de validação de uma regra de negócio do domínio."""


class BookNotFoundError(LookupError):
    """Levantado quando um identificador de livro não existe na coleção."""


@dataclass
class Book:
    id: str
    title: str
    author: str
    status: ReadingStatus = ReadingStatus.WANT_TO_READ
    started_at: date | None = None
    finished_at: date | None = None
    rating: int | None = None
    notes: str | None = None
    created_at: datetime = field(default_factory=datetime.now)


def new_book_id() -> str:
    return uuid.uuid4().hex[:8]


def create_book(title: str, author: str) -> Book:
    """Cria um novo Book validado, com status inicial 'quero ler' (FR-001..FR-003)."""
    title = (title or "").strip()
    author = (author or "").strip()
    if not title:
        raise ValidationError("O título do livro não pode ser vazio.")
    if not author:
        raise ValidationError("O autor do livro não pode ser vazio.")
    return Book(
        id=new_book_id(),
        title=title,
        author=author,
        status=ReadingStatus.WANT_TO_READ,
        created_at=datetime.now(),
    )


def update_status(book: Book, new_status: ReadingStatus) -> Book:
    """Atualiza o status preenchendo started_at/finished_at automaticamente (FR-005, FR-006)."""
    book.status = new_status
    today = date.today()
    if new_status == ReadingStatus.READING and book.started_at is None:
        book.started_at = today
    if new_status == ReadingStatus.READ and book.finished_at is None:
        book.finished_at = today
    return book


def set_rating(book: Book, rating: int) -> Book:
    """Define a nota de um livro; exige status 'lido' e nota entre 1 e 5 (FR-008)."""
    if book.status != ReadingStatus.READ:
        raise ValidationError(
            "Só é possível avaliar um livro com status 'lido'. "
            f"Status atual: '{book.status.label}'."
        )
    if rating < 1 or rating > 5:
        raise ValidationError("A nota deve ser um número entre 1 e 5.")
    book.rating = rating
    return book


def set_notes(book: Book, notes: str) -> Book:
    """Define a nota pessoal (texto livre) de um livro, independente do status (FR-009)."""
    book.notes = notes
    return book
