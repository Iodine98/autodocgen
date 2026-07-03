import sys

import pytest

from src.autodocgen import cli


def test_main_exits_nonzero_for_missing_path(monkeypatch, tmp_path, capsys):
    missing_path = tmp_path / "does_not_exist.py"
    monkeypatch.setattr(sys, "argv", ["autodocgen", str(missing_path)])
    with pytest.raises(SystemExit) as exc_info:
        cli.main()
    assert exc_info.value.code == 1
    assert "does not exist" in capsys.readouterr().err


def test_main_exits_nonzero_for_non_python_file(monkeypatch, tmp_path, capsys):
    non_python_file = tmp_path / "not_python.txt"
    non_python_file.write_text("hello")
    monkeypatch.setattr(sys, "argv", ["autodocgen", str(non_python_file)])
    with pytest.raises(SystemExit) as exc_info:
        cli.main()
    assert exc_info.value.code == 1
    assert "not a Python file" in capsys.readouterr().err


def test_main_requires_path_argument(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["autodocgen"])
    with pytest.raises(SystemExit) as exc_info:
        cli.main()
    assert exc_info.value.code == 2
