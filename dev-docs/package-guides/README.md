# Package Reference Guides for AI Agents

This folder contains **source-verified, version-specific API references** for Python packages and tools used across Talk Python projects. Each guide is distilled from actual source code — not training data or web searches — so the APIs, signatures, and patterns are accurate for the versions in use.

These guides are sourced from the [python-package-guides-for-agents](https://github.com/mikeckennedy/python-package-guides-for-agents) project.

## Why these exist

AI coding agents often hallucinate APIs, use deprecated patterns, or generate code based on stale training data. These local references solve that by giving agents verified documentation they can read directly — no web search required, no token-wasting round trips, no risk of outdated results.

## How to use them

**Before writing or modifying code that uses any of these packages, read the relevant guide.** It will give you correct API usage, accurate method signatures, and version-specific features.

## Available Guides

### Web Frameworks
| Guide | Package | Description |
|-------|---------|-------------|
| `quart_reference.md` | Quart | Async Python web microframework (asyncio reimplementation of Flask's API) |
| `flask_reference.md` | Flask | Python web microframework — Quart mirrors this API |
| `fastapi_reference.md` | FastAPI | Modern async web framework with automatic OpenAPI docs |
| `django_reference.md` | Django 6.1 | Full-featured web framework (models, ORM, views, admin, etc.) |
| `pyramid_reference.md` | Pyramid 2.x | Flexible web framework with traversal and URL dispatch routing |
| `robyn-reference.md` | Robyn | High-performance web framework with a Rust runtime |
| `nicegui_reference.md` | NiceGUI | Python UI framework built on FastAPI, Vue 3, and Quasar |

### Database & Data
| Guide | Package | Description |
|-------|---------|-------------|
| `pymongo_reference.md` | PyMongo 4.x | Official Python driver for MongoDB (sync and async APIs) |
| `mongoengine_reference.md` | MongoEngine 0.29 | Python Object-Document Mapper (ODM) for MongoDB |
| `pydantic_reference.md` | Pydantic 2.13 | Data validation and settings management using Python type hints |
| `dataclasswizard_reference.md` | Dataclass Wizard 0.39 | JSON to dataclass (de)serialization |

### HTTP & Networking
| Guide | Package | Description |
|-------|---------|-------------|
| `httpx_reference.md` | HTTPX 0.28 | Async/sync HTTP client with HTTP/2 support |
| `discordpy_reference.md` | discord.py 2.8 | Discord API wrapper for building bots |
| `listmonk_reference.md` | Listmonk | Python client for the self-hosted Listmonk email platform |

### Templates
| Guide | Package | Description |
|-------|---------|-------------|
| `chameleon-flask_reference.md` | chameleon-flask 0.6 | Chameleon template integration with Flask/Quart (`@template` decorator) |
| `chameleon-partials_reference.md` | chameleon_partials 0.1 | Partial template reuse (`${render_partial('path.pt')}`) |

### Infrastructure & Utilities
| Guide | Package | Description |
|-------|---------|-------------|
| `granian_reference.md` | Granian 2.7 | Rust-based HTTP server for Python ASGI/RSGI/WSGI apps |
| `docker_reference.md` | Docker | Container platform — Dockerfile, Compose, networking, volumes |
| `diskcache_reference.md` | DiskCache 5.6 | Persistent caching with SQLite backend |
| `tenacity_reference.md` | Tenacity | Retry decorator for flaky I/O operations |
| `loguru_reference.md` | Loguru 0.7 | Simple, pre-configured Python logging library |
| `content-types_reference.md` | content-types | File extension to MIME type mapping |
