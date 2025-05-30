# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python client library for the Listmonk email platform. The library provides a simplified interface to the Listmonk API, focusing on subscriber management, campaign operations, template handling, and transactional emails.

### Architecture

- **`listmonk/__init__.py`**: Main module entry point with public API exports
- **`listmonk/impl/__init__.py`**: Core implementation containing all API functions
- **`listmonk/models/__init__.py`**: Pydantic models for request/response data
- **`listmonk/urls.py`**: API endpoint URL constants
- **`listmonk/errors/__init__.py`**: Custom exception classes

The library uses a simple global state pattern for authentication (username/password stored globally) and builds on httpx for HTTP operations and Pydantic for data validation.

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

## Code Style and Conventions

- **Line length**: 120 characters (configured in ruff.toml)
- **Quote style**: Single quotes
- **Python version**: Supports 3.10+, targets 3.13
- **Dependencies**: httpx, pydantic, strenum
- **Import organization**: Group imports by stdlib, third-party, local with proper spacing

### Key Patterns

1. **Global State Management**: Authentication credentials are stored in module-level variables
2. **Pydantic Models**: All API data structures use Pydantic BaseModel for validation
3. **Error Handling**: Custom exceptions in `listmonk.errors` for validation and operation errors
4. **URL Constants**: All API endpoints defined in `urls.py` with format string placeholders
5. **Optional Timeouts**: All network operations accept optional `httpx.Timeout` configuration

### Function Naming Convention

- Functions follow snake_case
- Functions that fetch single items: `{resource}_by_{identifier}` (e.g., `subscriber_by_email`)
- Functions that fetch collections: `{resources}` (e.g., `subscribers`, `campaigns`)
- CRUD operations: `create_{resource}`, `update_{resource}`, `delete_{resource}`

## Testing and Examples

No formal test suite exists. The `example_client/client.py` serves as both documentation and integration testing, demonstrating all major API operations against a real Listmonk instance.