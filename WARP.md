# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a Python client library for the Listmonk email platform. The library provides a simplified interface to the Listmonk API, focusing on subscriber management, campaign operations, template handling, and transactional emails.

**Note**: This library covers a subset of the Listmonk API focused on common SaaS actions (subscribe, unsubscribe, segmentation). It doesn't cover all endpoints like creating lists programmatically or editing HTML templates for campaigns.

## Development Commands

### Install for Development
```bash
pip install -e .
```

### Code Quality
```bash
ruff check          # Lint with E, F, I rules
ruff format         # Format with 120 char limit, single quotes
```

### Testing
```bash
python example_client/client.py
```

The example client serves as both documentation and integration testing. Copy `example_client/settings-template.json` to `example_client/settings.json` and configure your Listmonk instance details.

## Architecture

### Module Structure
- **`listmonk/__init__.py`**: Main module entry point with public API exports
- **`listmonk/impl/__init__.py`**: Core implementation containing all API functions
- **`listmonk/models/__init__.py`**: Pydantic models for request/response data
- **`listmonk/urls.py`**: API endpoint URL constants with format placeholders
- **`listmonk/errors/__init__.py`**: Custom exception classes

### Key Patterns

1. **Global State Management**: Authentication credentials and base URL are stored in module-level variables in `impl/__init__.py`. Call `set_url_base()` and `login()` before using other functions.

2. **Function Naming Conventions**: 
   - Single items: `{resource}_by_{identifier}` (e.g., `subscriber_by_email`)
   - Collections: `{resources}` (e.g., `subscribers`, `campaigns`) 
   - CRUD: `create_{resource}`, `update_{resource}`, `delete_{resource}`

3. **HTTP & Validation**: All API calls use httpx with BasicAuth. Responses are validated and parsed through `_validate_and_parse_json_response()`. All network operations accept optional `httpx.Timeout` configuration.

4. **Pydantic Models**: All data structures use Pydantic BaseModel for validation. Models handle serialization of datetime fields and list conversions.

5. **Error Handling**: Custom exceptions in `listmonk.errors` for validation (`ValidationError`) and operation errors (`OperationNotAllowedError`).

## Configuration

- **Python Version**: Minimum 3.10, targets 3.13
- **Dependencies**: httpx, pydantic, strenum
- **Code Style**: 120 character lines, single quotes, ruff formatting
- **Ruff Rules**: E (pycodestyle errors), F (pyflakes), I (import sorting)

## Development Notes

### Authentication
As of Listmonk v4.0+, you must use API credentials (not regular user accounts). Configure these in your test settings.

### Testing Philosophy
No formal test suite exists. The `example_client/client.py` demonstrates all major operations and serves as integration testing. When adding new features, extend this example client to validate functionality.

### Global State
Functions depend on module-level authentication state. Always call `set_url_base()` and `login()` before other operations. Use `verify_login()` to check authentication status.