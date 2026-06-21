"""Testes de contrato: invocam readtrack.cli.main() ponta-a-ponta e validam
stdout/stderr/exit code, conforme contracts/cli-contract.md."""

import json

from readtrack.cli import EXIT_OK, EXIT_USAGE_ERROR, main


def run(capsys, argv):
    exit_code = main(argv)
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


# --- US1: add / list -------------------------------------------------------


def test_add_and_list_happy_path(readtrack_env, capsys):
    code, out, _ = run(capsys, ["add", "--title", "Duna", "--author", "Frank Herbert"])
    assert code == EXIT_OK
    assert "Duna" in out

    code, out, _ = run(capsys, ["list"])
    assert code == EXIT_OK
    assert "Duna" in out
    assert "quero ler" in out


def test_add_rejects_empty_title(readtrack_env, capsys):
    code, _, err = run(capsys, ["add", "--title", "  ", "--author", "Alguém"])
    assert code == EXIT_USAGE_ERROR
    assert "título" in err.lower()


def test_list_on_empty_collection_is_informative_not_error(readtrack_env, capsys):
    code, out, _ = run(capsys, ["list"])
    assert code == EXIT_OK
    assert "Nenhum livro" in out


def test_list_json_output(readtrack_env, capsys):
    run(capsys, ["add", "--title", "Duna", "--author", "Frank Herbert"])
    code, out, _ = run(capsys, ["list", "--json"])
    assert code == EXIT_OK
    data = json.loads(out)
    assert data[0]["title"] == "Duna"


# --- US2: status ------------------------------------------------------------


def _add_book(capsys) -> str:
    _, out, _ = run(capsys, ["add", "--title", "Duna", "--author", "Frank Herbert", "--json"])
    return json.loads(out)["id"]


def test_status_transitions_fill_dates(readtrack_env, capsys):
    book_id = _add_book(capsys)

    code, out, _ = run(capsys, ["status", book_id, "lendo"])
    assert code == EXIT_OK
    assert "lendo" in out

    code, out, _ = run(capsys, ["status", book_id, "lido"])
    assert code == EXIT_OK
    assert "lido" in out


def test_status_unknown_book_id_returns_error(readtrack_env, capsys):
    code, _, err = run(capsys, ["status", "naoexiste", "lendo"])
    assert code == EXIT_USAGE_ERROR
    assert "não" in err.lower() or "nenhum" in err.lower()


# --- US3: rate / note --------------------------------------------------------


def test_rate_requires_status_read(readtrack_env, capsys):
    book_id = _add_book(capsys)
    code, _, err = run(capsys, ["rate", book_id, "5"])
    assert code == EXIT_USAGE_ERROR
    assert "lido" in err.lower()


def test_rate_succeeds_after_marking_as_read(readtrack_env, capsys):
    book_id = _add_book(capsys)
    run(capsys, ["status", book_id, "lido"])
    code, out, _ = run(capsys, ["rate", book_id, "5"])
    assert code == EXIT_OK
    assert "5" in out


def test_rate_out_of_range_is_rejected(readtrack_env, capsys):
    book_id = _add_book(capsys)
    run(capsys, ["status", book_id, "lido"])
    code, _, err = run(capsys, ["rate", book_id, "9"])
    assert code == EXIT_USAGE_ERROR
    assert "nota" in err.lower()


def test_note_can_be_set_independent_of_status(readtrack_env, capsys):
    book_id = _add_book(capsys)
    code, out, _ = run(capsys, ["note", book_id, "Reler em alguns anos."])
    assert code == EXIT_OK
    assert book_id in out


# --- US4: search / list --status / stats ------------------------------------


def test_search_finds_by_title_or_author(readtrack_env, capsys):
    run(capsys, ["add", "--title", "Duna", "--author", "Frank Herbert"])
    run(capsys, ["add", "--title", "Outro Livro", "--author", "Outro Autor"])

    code, out, _ = run(capsys, ["search", "duna"])
    assert code == EXIT_OK
    assert "Duna" in out
    assert "Outro Livro" not in out


def test_list_filter_by_status(readtrack_env, capsys):
    book_id = _add_book(capsys)
    run(capsys, ["status", book_id, "lido"])
    run(capsys, ["add", "--title", "Outro", "--author", "Autor"])

    code, out, _ = run(capsys, ["list", "--status", "lido"])
    assert code == EXIT_OK
    assert "Duna" in out
    assert "Outro" not in out


def test_stats_with_no_ratings_shows_sem_avaliacoes(readtrack_env, capsys):
    code, out, _ = run(capsys, ["stats"])
    assert code == EXIT_OK
    assert "sem avaliações" in out


def test_stats_reflects_collection_state(readtrack_env, capsys):
    book_id = _add_book(capsys)
    run(capsys, ["status", book_id, "lido"])
    run(capsys, ["rate", book_id, "5"])

    code, out, _ = run(capsys, ["stats"])
    assert code == EXIT_OK
    assert "Livros lidos: 1" in out
    assert "5.0" in out


# --- remove ------------------------------------------------------------------


def test_remove_existing_book(readtrack_env, capsys):
    book_id = _add_book(capsys)
    code, out, _ = run(capsys, ["remove", book_id])
    assert code == EXIT_OK
    assert book_id in out

    code, out, _ = run(capsys, ["list"])
    assert "Nenhum livro" in out


def test_remove_unknown_book_id_returns_error(readtrack_env, capsys):
    code, _, err = run(capsys, ["remove", "naoexiste"])
    assert code == EXIT_USAGE_ERROR


# --- US5: export / import ----------------------------------------------------


def test_export_and_import_roundtrip(readtrack_env, capsys, tmp_path):
    book_id = _add_book(capsys)
    run(capsys, ["status", book_id, "lido"])
    run(capsys, ["rate", book_id, "5"])
    run(capsys, ["note", book_id, "Ótimo livro"])

    backup_path = tmp_path / "backup.json"
    code, out, _ = run(capsys, ["export", str(backup_path)])
    assert code == EXIT_OK
    assert backup_path.exists()

    run(capsys, ["remove", book_id])
    code, out, _ = run(capsys, ["list"])
    assert "Nenhum livro" in out

    code, out, _ = run(capsys, ["import", str(backup_path)])
    assert code == EXIT_OK

    code, out, _ = run(capsys, ["list", "--json"])
    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["id"] == book_id
    assert data[0]["rating"] == 5
    assert data[0]["notes"] == "Ótimo livro"


def test_import_missing_file_returns_error(readtrack_env, capsys, tmp_path):
    missing = tmp_path / "nao-existe.json"
    code, _, err = run(capsys, ["import", str(missing)])
    assert code == EXIT_USAGE_ERROR
    assert "não encontrado" in err.lower() or "not found" in err.lower()


def test_import_malformed_file_returns_error(readtrack_env, capsys, tmp_path):
    malformed = tmp_path / "malformado.json"
    malformed.write_text("{ isso nao e json valido ]", encoding="utf-8")
    code, _, err = run(capsys, ["import", str(malformed)])
    assert code == EXIT_USAGE_ERROR
    assert "malformado" in err.lower()
