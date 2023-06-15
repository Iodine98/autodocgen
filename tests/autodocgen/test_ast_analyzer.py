import base64
import secrets
from _ast import AST
from pathlib import Path

import pytest

from src.autodocgen.ast_analyzer import ASTAnalyzer


def generate_random_b64_string(length: int):
    random_bytes = secrets.token_bytes(length)
    random_b64 = base64.b64encode(random_bytes).decode("utf-8")
    return random_b64


def test_raise_env_error(monkeypatch):
    monkeypatch.delenv("OPENAI_KEY", raising=False)
    with pytest.raises(EnvironmentError) as env_err:
        ASTAnalyzer()
    assert str(env_err.value) == "OPENAI_KEY is missing"


@pytest.fixture
def ast_analyzer(monkeypatch):
    monkeypatch.setenv("OPENAI_KEY", generate_random_b64_string(40))
    ast_analyser = ASTAnalyzer()
    return ast_analyser


@pytest.fixture
def load_from_file(ast_analyzer):
    ast_analyzer.load_ast_from_file("./src/autodocgen/ast_analyzer.py")


def test_load_from_file(ast_analyzer, load_from_file):
    assert isinstance(ast_analyzer.tree, AST)


def test_write_ast_to_file(ast_analyzer, load_from_file):
    file_path = Path("./src/autodocgen/ast_analyzer.py")
    file_contents: str = ast_analyzer.write_file_from_ast(file_path, str_return=True)
    with open(file_path, "r") as code_file:
        expected_code = code_file.read()

    # Assert that the contents match the expected value
    assert file_contents == expected_code
