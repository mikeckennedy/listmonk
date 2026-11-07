# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
* `update_subscriber()` keeps the subscriber's current status unless you pass `status=`. It used to default to `enabled`, so passing back a disabled or blocklisted subscriber to change their name quietly put them back on the mailing lists. `enable_subscriber()`, `disable_subscriber()`, and `block_subscriber()` pass their status explicitly and behave as before. If you relied on the implicit re-enable, pass `status=SubscriberStatuses.enabled`
* `subscriber_by_id()` now calls Listmonk's direct `GET /api/subscribers/{id}` endpoint instead of a SQL `query=` filter, so it no longer needs the `subscribers:sql_query` permission. Listmonk answers an unknown ID with HTTP 400, which the function still reports as `None`; any other 4xx/5xx raises `httpx2.HTTPStatusError` as before
* `create_campaign()` no longer lowercases `from_email`, so a display name such as `Newsletter <news@example.com>` is sent as written (surrounding whitespace is still stripped). `update_campaign()` already passed the address through untouched
* `list_by_id()` raises `listmonk.errors.ValidationError` instead of a bare `Exception` when the server's result set does not contain the requested list (the listmonk#2117 workaround path). `ValidationError` subclasses `Exception`, so existing `except Exception` handlers still catch it

### Fixed
* `subscriber_by_email()` and `subscriber_by_uuid()` now send the lookup value as a quoted SQL literal with embedded quotes escaped, and URL-encode the whole filter. Listmonk runs the `query` parameter as a raw SQL expression, so an attacker-controlled address such as `x' OR true --` used to match the first subscriber on the server instead of nobody, and `delete_subscriber(email)` would then have deleted that subscriber
* `send_transactional_email()` reads attachment bytes up front instead of handing open file objects to httpx2, which were never closed
* `test_campaign()` now sends the campaign's `altbody` and custom `headers` with the test request. Listmonk copies both from the request onto the test message, so the test copy used to arrive without the plain-text twin and without the custom headers the real send carries. Media IDs are deliberately not sent: the server keeps the stored attachments and would append duplicates
* `set_url_base()` strips surrounding whitespace before removing the trailing slash, so `'https://example.com/ '` no longer keeps its slash
* `tests/test_type_check.py` now passes the running interpreter's environment to `ty check --python`, so the type gate finds the project's `venv/` (ty only auto-discovers `.venv`) instead of reporting every third-party import as unresolved when the venv is not activated
* `scripts/build_docs.py` refuses to mirror a site that is missing `llms.txt`, `llms-full.txt`, `skill.md`, the `.well-known/agent-skills` files, `robots.txt`, or `sitemap.xml`, since Great Docs reports success even when it skips them

### Documentation
* Replaced the generated agent skill with a hand-written `skills/listmonk/SKILL.md` (wired through `skill.file` in `great-docs.yml`) that covers the rules of the package: call order, the raises-versus-returns-False error model, transactional subscriber modes, campaign status transitions, Go template syntax, and the permission behind the 403. `skill_extra_body.md` and the gotcha/decision-table lists in `great-docs.yml` folded into it
* Corrected the `test_campaign()` docs: Listmonk answers HTTP 400 "No known subscribers to test." when none of the addresses are subscribers, which the client raises as `httpx2.HTTPStatusError`; it does not silently send nothing. A test pins the behaviour
* README: documented `test_campaign()`, `start/pause/cancel_campaign()`, `subscriber_mode`, and multi-recipient transactional sends, which had only been in the changelog; added an Error handling section (what raises, what returns `False` or `None`, timeouts) and FAQ entries for `OperationNotAllowedError` and the campaign-test 400; switched the media example to an image, which is all a default server accepts
* Every public function, model, and exception now has an Examples section, so the reference pages and `llms-full.txt` show canonical usage; `update_campaign()` notes that dropping a past `send_at` returns a scheduled campaign to draft
* Package docstring lists the entry points (functions, `models`, `errors`, `timeout_config`, `SSL_CERT_FILE`/`SSL_CERT_DIR`); changelog compare links added for 0.5.31 and 0.6.32

## [0.6.32] - 2026-10-17

### Added
* `subscriber_mode` support in `send_transactional_email()`: pass `'external'` to email people who are not subscribers (no more creating a temporary subscriber, sending, then deleting it) or `'fallback'` to look the recipient up but send anyway if they aren't found. The field is omitted when unset, so requests to older servers are unchanged. In these modes only `{{ .Subscriber.Email }}` is populated, so pass anything else the template needs via `template_data` and read it as `{{ .Tx.Data.* }}`. Thank you [@waza-ari](https://github.com/waza-ari)
* `send_transactional_email()` now takes a list of addresses as its first argument to reach several recipients in one call, e.g. `send_transactional_email(['a@x.com', 'b@x.com'], template_id=3)`. A single string still maps to the server's `subscriber_email` field and a list to `subscriber_emails`, so the two fields the API rejects together cannot both be sent. Thank you [@waza-ari](https://github.com/waza-ari)

## [0.5.31] - 2026-07-31

### Added
* Type checking with [ty](https://github.com/astral-sh/ty) as the authoritative checker: a `ty.toml` config, a `ty` dev dependency, and `tests/test_type_check.py`, which fails the suite on any diagnostic (and skips when ty isn't installed). The tree is at zero diagnostics, checked against Python 3.10 — the floor of the supported range — so nothing newer than 3.10 slips into the public API

### Fixed
* Fixed the type errors and removed the 13 stale `# type: ignore` comments that `ty check` reported. Two were real latent crashes in `example_client/client.py`, which used a subscriber and its UUID without checking either for `None`; the example now guards once, up front, instead of suppressing the warnings

## [0.5.30] - 2026-07-31

### Added
* Campaign sending support, covering the two endpoints that actually deliver mail: `test_campaign(campaign_id, emails)` sends a one-off test copy to specific subscriber addresses (`POST /api/campaigns/{id}/test`) without touching the campaign or its stats, and `set_campaign_status(campaign_id, status)` moves a campaign through its lifecycle (`PUT /api/campaigns/{id}/status`) — this is how a draft is started, since `update_campaign()` cannot change status
* `start_campaign()`, `pause_campaign()`, and `cancel_campaign()` convenience wrappers over `set_campaign_status()`, in the spirit of `enable_subscriber()` / `disable_subscriber()` / `block_subscriber()`
* `models.CampaignStatuses` enum (`draft`, `scheduled`, `running`, `paused`, `cancelled`, `finished`), so an invalid status is caught client-side instead of surfacing as a Postgres enum error in an HTTP 500

## [0.4.3] - 2026-06-11

### Added
* Enrich the PyPI package metadata with a broader set of keywords (listmonk, email-marketing, campaigns, subscribers, transactional-email, etc.) for better discoverability

### Changed
* Exclude the `tests` directory from the published wheel and sdist, shrinking the installed package

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

[unreleased]: https://github.com/mikeckennedy/listmonk/compare/v0.6.32...HEAD
[0.6.32]: https://github.com/mikeckennedy/listmonk/compare/v0.5.31...v0.6.32
[0.5.31]: https://github.com/mikeckennedy/listmonk/compare/v0.4.3...v0.5.31
[0.4.3]: https://github.com/mikeckennedy/listmonk/compare/v0.4.2...v0.4.3
[0.4.2]: https://github.com/mikeckennedy/listmonk/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/mikeckennedy/listmonk/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/mikeckennedy/listmonk/compare/v0.3.13...v0.4.0
[0.3.13]: https://github.com/mikeckennedy/listmonk/compare/v0.3.12...v0.3.13
[0.3.12]: https://github.com/mikeckennedy/listmonk/compare/v0.3.11...v0.3.12
[0.3.11]: https://github.com/mikeckennedy/listmonk/compare/v0.3.10...v0.3.11
[0.3.10]: https://github.com/mikeckennedy/listmonk/compare/v0.3.9...v0.3.10
[0.3.9]: https://github.com/mikeckennedy/listmonk/compare/v0.3.8...v0.3.9
[0.3.8]: https://github.com/mikeckennedy/listmonk/releases/tag/v0.3.8

