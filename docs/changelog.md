# Changelog

This changelog is generated automatically from [GitHub Releases](https://github.com/mikeckennedy/listmonk/releases).


# v0.4.1

*2026-06-03* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.4.1)


## \[0.4.1\] - 2026-06-03


### Changed

- Migrate the HTTP backend from `httpx` to [`httpx2`](https://github.com/pydantic/httpx2), the Pydantic-maintained fork, after the original `httpx` project paused releases and locked down its issue tracker. `httpx2` is imported internally as `httpx`, so the public API and all call sites are unchanged.
- TLS certificates are now validated against the operating system trust store (via `truststore`, the `httpx2` default) instead of the bundled `certifi` CA list. If you self-host Listmonk behind a custom or corporate CA, install that CA in your OS trust store or set `SSL_CERT_FILE` / `SSL_CERT_DIR`. See the new SSL entry in the README F.A.Q.
- If you pass a custom `timeout_config`, construct it with `httpx2.Timeout(...)` (now the bundled dependency) instead of `httpx.Timeout(...)`.


# v0.4.0

*2026-04-08* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.4.0)


## \[0.4.0\] - 2026-04-08


### Added

- Add `altbody` support to [send_transactional_email()](reference/send_transactional_email.html#listmonk.send_transactional_email) for multipart HTML transactional emails. Thank you [<span class="citation" cites="neilime">@neilime</span>](https://github.com/neilime)


# v0.3.13

*2026-04-04* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.3.13)


## \[0.3.13\] - 2026-04-03


### Fixed

- Fix [confirm_optin()](reference/confirm_optin.html#listmonk.confirm_optin) returning `False` on non-English Listmonk instances by using HTTP status codes instead of hardcoded English response strings (fixes [\#23](https://github.com/mikeckennedy/listmonk/issues/23))


# v0.3.12

*2026-04-04* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.3.12)

Make subscriber name optional, bump version to 0.3.12 to match Listmonk API/UI behavior (fixes [\#15](https://github.com/mikeckennedy/listmonk/issues/15))

This update aligns the SDK with the Listmonk API and UI by making the `name` field optional for subscribers. The change propagates through the data models ([Subscriber](reference/models.Subscriber.html#listmonk.models.Subscriber), [CreateSubscriberModel](reference/models.CreateSubscriberModel.html#listmonk.models.CreateSubscriberModel)) and the [create_subscriber()](reference/create_subscriber.html#listmonk.create_subscriber) helper. The changelog is updated to reflect version 0.3.12, and the release comparison links are adjusted accordingly.


# v0.3.11

*2026-04-04* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.3.11)


## \[0.3.11\] - 2026-04-03


### Fixed

- Fix campaign creation failing with listmonk server 6.0.0 - `headers` field now correctly uses a list of dictionaries instead of a plain dictionary (PR [\#28](https://github.com/mikeckennedy/listmonk/issues/28))


# v0.3.10

*2026-01-28* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.3.10)


## \[0.3.10\] - 2026-01-28


### Added

- Add [update_list](reference/update_list.html#listmonk.update_list) function (thanks [<span class="citation" cites="ChrisH861">@ChrisH861</span>](https://github.com/ChrisH861), PR [\#27](https://github.com/mikeckennedy/listmonk/issues/27))


# v0.3.9

*2026-01-06* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.3.9)


## \[0.3.9\] - 2026-01-05


### Added

- Add add_subscribers_to_lists function (thanks [<span class="citation" cites="MochaSteve256">@MochaSteve256</span>](https://github.com/MochaSteve256))


### Changed

- Loosen some of the types to allow more flexible usage (avoid type errors when DTOs/ViewModels/etc have VALUE\|None typing but are known to be in a good state)
- Refactor client implementation to improve organization and maintainability


# v0.3.8

*2025-10-22* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.3.8)


### Added

- Support for subject parameter in transactional templates (PR [\#24](https://github.com/mikeckennedy/listmonk/issues/24))
- FAQ section to README.md (PR [\#22](https://github.com/mikeckennedy/listmonk/issues/22))
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

- Custom exception renamed from `FileNotFoundError` to [ListmonkFileNotFoundError](reference/errors.ListmonkFileNotFoundError.html#listmonk.errors.ListmonkFileNotFoundError) to avoid builtin conflict
- Non-string to string types in `__all__` exports
- Type inference error in code fragments

Thanks [<span class="citation" cites="neilime">@neilime</span>](https://github.com/neilime) and [<span class="citation" cites="obrizan">@obrizan</span>](https://github.com/obrizan) for the PRs.


# v0.3.7

*2025-05-24* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.3.7)

Restores custom header functionality for [send_transactional_email()](reference/send_transactional_email.html#listmonk.send_transactional_email) And create/delete list was, well, deleted.

It looks like this was some kind of failed merge, maybe. I'm not sure what happened here. Sorry folks.


# v0.3.6

*2025-05-20* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.3.6)

Bump version to fix project definition. strenum wasn't included in the pyproject.toml's dependencies. No functional changes.


# v0.3.5

*2025-05-18* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.3.5)

Add an optional timeout parameter (`httpx.Timeout`) for all network operations.


# v0.3.4

*2025-05-07* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.3.4)

Adds new features from two recent PRs:

- Allow to send headers to the /api/tx endpoint. https://github.com/mikeckennedy/listmonk/pull/20
- Create and delete lists. https://github.com/mikeckennedy/listmonk/pull/19


# v0.3.3

*2024-12-01* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.3.3)

Adds support for this library on Python 3.10 by replacing `enum.StrEnum` with [github.com/irgeek/StrEnum](https://github.com/irgeek/StrEnum).


# v0.3.0

*2024-11-12* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.3.0)

Adds two new features:

- 📨 Manage campaign (bulk) emails from the API.
- 🎨 Edit and create templates to control the over all look and feel of campaigns.

Thank you [<span class="citation" cites="pastorhudson">@pastorhudson</span>](https://github.com/pastorhudson) for the PRs.


# v0.2.1

*2024-10-29* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.2.1)

This release updates the library to work with Listmonk 4.0+ which was released yesterday.


# v0.1.8

*2024-04-06* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.1.8)

Bug fix: Searching for users with `listmonk.all_subscribers()` with a query parameter crashes (on the server, should be 400 but here's the fix nonetheless).


# v0.1.7

*2024-02-02* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.1.7)

Add ability to add attachments to transactional mails, see [\#5](https://github.com/mikeckennedy/listmonk/issues/5)


# v0.1.6

*2024-01-29* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.1.6)

Make from email option on transactional emails.


# v0.1.5

*2024-01-24* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.1.5)

Loosen some pydantic constraints for some situations.


# v0.1.4

*2024-01-22* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.1.4)

Added doc strings for most data and methods and specific exception types.


# v0.1.3

*2024-01-21* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.1.3)

Fix bug where emails with a `+` wouldn't work on retrieval.


# v0.1.2

*2024-01-21* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.1.2)

Added opt-in / confirm subscription method.
