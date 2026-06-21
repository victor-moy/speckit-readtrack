import sqlite3
from pathlib import Path

import pytest

from readtrack import storage


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "readtrack-test.db"


@pytest.fixture
def conn(db_path: Path) -> sqlite3.Connection:
    connection = storage.init_db(db_path)
    yield connection
    connection.close()


@pytest.fixture
def readtrack_env(monkeypatch: pytest.MonkeyPatch, db_path: Path) -> Path:
    """Isola o comando CLI para usar um banco SQLite temporário por teste."""
    monkeypatch.setenv("READTRACK_DB_PATH", str(db_path))
    return db_path
