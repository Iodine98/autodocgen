# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

autodocgen is a small Python CLI tool that automatically generates Google-style
Pydoc docstrings for Python source files using an OpenAI chat model. It parses a
file's AST, sends each function/class definition to the OpenAI API, and injects
the returned docstring back into the AST before writing formatted code back out.

## Setup

- Dependency management is via Poetry (`pyproject.toml` / `poetry.lock`). Install with `poetry install`.
- Requires Python `^3.9`.
- Requires an `OPENAI_KEY` environment variable (loaded via `python-dotenv` from a `.env` file). `ASTAnalyzer.__init__` raises `EnvironmentError` if it is missing.
- Uses the legacy `openai` `^0.27.7` SDK (`openai.ChatCompletion.create`, `openai.error.RateLimitError`), not the current `openai` Python client.

## Running

- CLI entry point: `autodocgen` (declared in `pyproject.toml` under `[tool.poetry.scripts]`, backed by `src/autodocgen/cli.py:main`).
  - `autodocgen <path>` — process a single `.py` file or recursively walk a directory.
  - `-i` / `--overwrite` / `--inplace` — overwrite the original file instead of writing a copy.
  - `-s` / `--suffix` — suffix appended to the output filename stem when not overwriting (default `_doc`).
  - `--disable_tqdm` — disable the progress bar.
- `script.py` is a standalone example showing direct use of `ASTAnalyzer` and `FileVisitor` without the CLI.

## Tests

- `pytest` (tests live in `tests/autodocgen/`, mirroring `src/autodocgen/`).
- Run with `pytest` or `poetry run pytest` from the repo root — tests import via the `src.autodocgen` path, so run them from the project root.
- Tests stub `OPENAI_KEY` via `monkeypatch` rather than calling the real OpenAI API.

## Architecture

- `src/autodocgen/ast_analyzer.py` — `ASTAnalyzer`: owns the OpenAI chat session (message history, model kwargs), loads/parses a file's AST, calls the model to obtain a docstring for a given source snippet (`obtain_pydoc`), extracts the docstring from the model's response (handles `"""`, `'''`, or ` ``` ` fencing), inserts it into the AST (`add_docstring_to_ast`), and writes the modified AST back out through `black` for formatting (`write_file_from_ast`).
- `src/autodocgen/file_visitor.py` — AST traversal built on `ast.NodeTransformer`:
  - `ClassVisitor` / `MethodVisitor` visit `ClassDef` / `FunctionDef` nodes and delegate to `FileVisitor.visit_def`.
  - `FileVisitor.visit_def` converts a node back to source via `astor`, requests a docstring through `ASTAnalyzer.obtain_pydoc_wrapper`, and writes it into the node. It retries on `RateLimitError` (random backoff) and `APIConnectionError` (30s wait).
  - `FileVisitor.visit` runs the class pass and function pass separately over the tree, clearing the chat message history (`ast_analyzer.remove_messages`) between passes so each definition gets a fresh prompt context.
- `src/autodocgen/cli.py` — argument parsing and directory walking (`process_python_file`, `process_directory`); sleeps between files/directories to stay under OpenAI rate limits.
- The three modules are tightly coupled by design: `ASTAnalyzer` and `FileVisitor` hold references to each other and are meant to be constructed together (see `script.py` for the intended wiring).

## Conventions

- Docstrings in this codebase itself follow Google style (per `README.md`'s stated model prompt), though some files mix `:param:`/Sphinx-style docstrings — match whichever style is already used in the file you're editing.
- `pylint` is configured as a dev dependency; there is no committed lint config beyond defaults.
