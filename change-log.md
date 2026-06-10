# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.4.2] - 2026-06-09

### Added
* Add media upload and campaign attachment support: new `upload_media()` function and `Media` model, plus a `media_ids` parameter on `create_campaign()` and `update_campaign()`. Updates preserve a campaign's existing attachments unless `media_ids` is passed explicitly. (fixes #16)
* Documentation site at https://mkennedy.codes/docs/listmonk/ generated from the docstrings with Great Docs
* Ship a `py.typed` marker (and the `Typing :: Typed` classifier) so mypy/pyright type-check against the library's annotations
* `create_list()`, `update_list()`, and `delete_list()` now accept the optional `timeout_config` parameter like every other network call (`delete_list()` previously hardcoded a 30-second timeout; all three now default to 10 seconds)

### Changed
* Import `httpx2` directly instead of aliasing it as `httpx`, so signatures, docstrings, and the docs site all show `httpx2.Timeout` / `httpx2.HTTPStatusError` — the names users actually import
* Tighten public signatures to match documented behavior: required parameters are no longer `Optional` (`create_campaign(name, subject)`, `create_template(name, body)`, `delete_campaign(campaign_id)`, `delete_template(template_id)`, `set_default_template(template_id)`, `confirm_optin(...)`), and functions that can never return `None` no longer claim `Optional` returns (`list_by_id`, `campaign_preview_by_id`, `template_preview_by_id`, `create_campaign`, `create_template`, `create_list`, `update_list`)
* Fix the `headers` parameter annotation on `create_campaign()` — it is a list of single-entry dicts, not a dict
* Accuracy pass over docstrings, the README, and the example client (corrected TLS/certifi guidance, README samples that would not run as written, stale claims about unimplemented list/template APIs)

### Fixed
* Fix `update_list()` sending the list type as `list_type` instead of `type`, so changing a list's type now actually takes effect
* Fix `Subscriber.model_dump()` crashing on server-populated subscribers (list-membership dicts and a `None` `updated_at` now serialize cleanly)
* Fix the `list_by_id()` workaround for listmonk#2117 crashing with `AttributeError` when the server returns a result set (dict access instead of attribute access)
* Fix repeat `login()` calls returning `True` without re-validating the new credentials against the server

## [0.4.1] - 2026-06-03

### Changed
* Migrate the HTTP backend from `httpx` to [`httpx2`](https://github.com/pydantic/httpx2), the Pydantic-maintained fork, after the original `httpx` project paused releases and locked down its issue tracker. `httpx2` is imported internally as `httpx`, so the public API and all call sites are unchanged.
* TLS certificates continue to be validated against the bundled `certifi` CA list (the `httpx2` default). If you self-host Listmonk behind a custom or corporate CA, set `SSL_CERT_FILE` / `SSL_CERT_DIR` to point at your CA bundle. See the SSL entry in the README F.A.Q.
* If you pass a custom `timeout_config`, construct it with `httpx2.Timeout(...)` (now the bundled dependency) instead of `httpx.Timeout(...)`.

## [0.4.0] - 2026-04-08

### Added
* Add `altbody` support to `send_transactional_email()` for multipart HTML transactional emails

## [0.3.13] - 2026-04-03

### Fixed
* Fix `confirm_optin()` returning `False` on non-English Listmonk instances by using HTTP status codes instead of hardcoded English response strings (fixes #23)

## [0.3.12] - 2026-04-03

### Changed
* Make subscriber `name` field optional in `Subscriber`, `CreateSubscriberModel`, and `create_subscriber()` to match the Listmonk API/UI behavior (fixes #15)

## [0.3.11] - 2026-04-03

### Fixed
* Fix campaign creation failing with listmonk server 6.0.0 - `headers` field now correctly uses a list of dictionaries instead of a plain dictionary (PR #28)

## [0.3.10] - 2026-01-28

### Added
* Add update_list function (thanks @ChrisH861, PR #27)

## [0.3.9] - 2026-01-05

### Added
* Add add_subscribers_to_lists function (thanks @MochaSteve256)

### Changed
* Loosen some of the types to allow more flexible usage (avoid type errors when DTOs/ViewModels/etc have VALUE|None typing but are known to be in a good state)
* Refactor client implementation to improve organization and maintainability

## [0.3.8] - 2025-10-22

### Added
- Support for subject parameter in transactional templates (PR #24)
- FAQ section to README.md (PR #22)
- Four new API methods to the public interface
- CLAUDE.md with project overview, development commands, code style, and key patterns
- WARP.md documentation
- Ruff formatting configuration

### Changed
- Extensive type annotation improvements for better IDE support (PyLance/VS Code)
- HTTP response validation and parsing refactored for better error handling
- Headers type fix: now properly uses string values instead of list of dictionaries
- Code formatting with ruff throughout the codebase
- Documentation improvements in README.md

### Fixed
- Custom exception renamed from `FileNotFoundError` to `ListmonkFileNotFoundError` to avoid builtin conflict
- Non-string to string types in `__all__` exports
- Type inference error in code fragments

[unreleased]: https://github.com/mikeckennedy/listmonk/compare/v0.4.2...HEAD
[0.4.2]: https://github.com/mikeckennedy/listmonk/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/mikeckennedy/listmonk/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/mikeckennedy/listmonk/compare/v0.3.13...v0.4.0
[0.3.13]: https://github.com/mikeckennedy/listmonk/compare/v0.3.12...v0.3.13
[0.3.12]: https://github.com/mikeckennedy/listmonk/compare/v0.3.11...v0.3.12
[0.3.11]: https://github.com/mikeckennedy/listmonk/compare/v0.3.10...v0.3.11
[0.3.10]: https://github.com/mikeckennedy/listmonk/compare/v0.3.9...v0.3.10
[0.3.9]: https://github.com/mikeckennedy/listmonk/compare/v0.3.8...v0.3.9
[0.3.8]: https://github.com/mikeckennedy/listmonk/releases/tag/v0.3.8

