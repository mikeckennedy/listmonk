# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python client library for the Listmonk email platform. The library provides a simplified interface to the Listmonk API, focusing on subscriber management, campaign operations, template handling, media uploads, and transactional emails.

### Architecture

- **`listmonk/__init__.py`**: Main module entry point with public API exports
- **`listmonk/impl/__init__.py`**: Core implementation containing all API functions
- **`listmonk/models/__init__.py`**: Pydantic models for request/response data
- **`listmonk/urls.py`**: API endpoint URL constants
- **`listmonk/errors/__init__.py`**: Custom exception classes

The library uses a simple global state pattern for authentication (username/password stored globally) and builds on httpx2 for HTTP operations and Pydantic for data validation.

## Development Commands

### Linting and Code Quality
```bash
ruff check
ruff format
```

### Running the Example Client
```bash
python example_client/client.py
```

### Rebuilding the Docs Site
```bash
./venv/bin/python scripts/build_docs.py
```
The committed `docs/` directory is a generated static site built from docstrings by great-docs (installed via the `dev` extra: `pip install -e .[dev]`, requires Python 3.11+). The script runs `great-docs build` and mirrors the `great-docs/_site/` output into `docs/`. Rebuild whenever a public docstring or signature changes. Never hand-edit files under `docs/` — fix the source docstrings instead. Use `scripts/serve_docs.py` to preview the site locally.

## Code Style and Conventions

- **Line length**: 120 characters (configured in ruff.toml)
- **Quote style**: Single quotes
- **Python version**: Supports 3.10+ (classifiers through 3.15), ruff targets 3.13
- **Dependencies**: httpx2, pydantic, strenum
- **Import organization**: Group imports by stdlib, third-party, local with proper spacing (enforced by ruff `"I"` rule)

### Key Patterns

1. **Global State Management**: Authentication credentials are stored in module-level variables
2. **Pydantic Models**: All API data structures use Pydantic BaseModel for validation
3. **Error Handling**: Custom exceptions in `listmonk.errors`: `ValidationError`, `OperationNotAllowedError`, and `ListmonkFileNotFoundError`
4. **URL Constants**: All API endpoints defined in `urls.py` with format string placeholders
5. **Optional Timeouts**: All network operations accept optional `httpx2.Timeout` configuration
6. **Code Organization**: Functions in `impl/__init__.py` are grouped with `# region` / `# endregion` comments
7. **Multipart Uploads**: Media uploads and transactional email attachments use httpx2 multipart form-data encoding
8. **Typed Package**: The package ships `py.typed`, so public annotations are contractual for downstream type checkers

### Function Naming Convention

- Functions follow snake_case
- Functions that fetch single items: `{resource}_by_{identifier}` (e.g., `subscriber_by_email`)
- Functions that fetch collections: `{resources}` (e.g., `subscribers`, `campaigns`)
- CRUD operations: `create_{resource}`, `update_{resource}`, `delete_{resource}`

## Package Reference Guides

The `dev-docs/package-guides/` directory (from [python-package-guides-for-agents](https://github.com/mikeckennedy/python-package-guides-for-agents)) contains detailed API reference docs for key dependencies and the Listmonk server API. Consult these when working with httpx2 (the `httpx_reference` guide still documents the near-identical httpx 0.28 API), Pydantic, or the Listmonk REST API rather than relying solely on training data.

## Testing and Examples

### Unit Tests
```bash
./venv/bin/python -m pytest
```
Tests live in `tests/` and exercise the public API end to end against an in-memory fake of the Listmonk HTTP API — no server or network needed. `tests/conftest.py` provides the `fake_server` fixture (patches the httpx2 verbs, returns real `httpx2.Response` objects, and records every request for assertions) and the `logged_in` fixture (puts the module-level auth state into a logged-in condition). Canned response payloads come from `tests/factories.py`. When adding or changing a public function, add a behavior-level test: register the canned server response, call the public function, and assert on the return value and/or the recorded outbound request.

### Integration Example
The `example_client/client.py` serves as both documentation and integration testing, demonstrating all major API operations against a real Listmonk instance.