# Changelog

This changelog is generated automatically from [GitHub Releases](https://github.com/mikeckennedy/listmonk/releases).


# v0.7.33

*2026-11-07* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.7.33)


### Changed

- [update_subscriber()](reference/update_subscriber.html#listmonk.update_subscriber) keeps the subscriber's current status unless you pass `status=`. It used to default to [enabled](reference/models.SubscriberStatuses.html#listmonk.models.SubscriberStatuses.enabled), so passing back a disabled or blocklisted subscriber to change their name quietly put them back on the mailing lists. [enable_subscriber()](reference/enable_subscriber.html#listmonk.enable_subscriber), [disable_subscriber()](reference/disable_subscriber.html#listmonk.disable_subscriber), and [block_subscriber()](reference/block_subscriber.html#listmonk.block_subscriber) pass their status explicitly and behave as before. If you relied on the implicit re-enable, pass `status=SubscriberStatuses.enabled`
- [subscriber_by_id()](reference/subscriber_by_id.html#listmonk.subscriber_by_id) now calls Listmonk's direct `GET /api/subscribers/{id}` endpoint instead of a SQL `query=` filter, so it no longer needs the `subscribers:sql_query` permission. Listmonk answers an unknown ID with HTTP 400, which the function still reports as `None`; any other 4xx/5xx raises `httpx2.HTTPStatusError` as before
- [create_campaign()](reference/create_campaign.html#listmonk.create_campaign) no longer lowercases `from_email`, so a display name such as `Newsletter <news@example.com>` is sent as written (surrounding whitespace is still stripped). [update_campaign()](reference/update_campaign.html#listmonk.update_campaign) already passed the address through untouched
- [list_by_id()](reference/list_by_id.html#listmonk.list_by_id) raises [listmonk.errors.ValidationError](reference/errors.ValidationError.html#listmonk.errors.ValidationError) instead of a bare `Exception` when the server's result set does not contain the requested list (the listmonk[\#2117](https://github.com/mikeckennedy/listmonk/issues/2117) workaround path). [ValidationError](reference/errors.ValidationError.html#listmonk.errors.ValidationError) subclasses `Exception`, so existing `except Exception` handlers still catch it


### Fixed

- [subscriber_by_email()](reference/subscriber_by_email.html#listmonk.subscriber_by_email) and [subscriber_by_uuid()](reference/subscriber_by_uuid.html#listmonk.subscriber_by_uuid) now send the lookup value as a quoted SQL literal with embedded quotes escaped, and URL-encode the whole filter. Listmonk runs the `query` parameter as a raw SQL expression, so an attacker-controlled address such as `x' OR true --` used to match the first subscriber on the server instead of nobody, and `delete_subscriber(email)` would then have deleted that subscriber
- [send_transactional_email()](reference/send_transactional_email.html#listmonk.send_transactional_email) reads attachment bytes up front instead of handing open file objects to httpx2, which were never closed
- [test_campaign()](reference/test_campaign.html#listmonk.test_campaign) now sends the campaign's `altbody` and custom `headers` with the test request. Listmonk copies both from the request onto the test message, so the test copy used to arrive without the plain-text twin and without the custom headers the real send carries. Media IDs are deliberately not sent: the server keeps the stored attachments and would append duplicates
- [set_url_base()](reference/set_url_base.html#listmonk.set_url_base) strips surrounding whitespace before removing the trailing slash, so `'https://example.com/ '` no longer keeps its slash
- `tests/test_type_check.py` now passes the running interpreter's environment to `ty check --python`, so the type gate finds the project's `venv/` (ty only auto-discovers `.venv`) instead of reporting every third-party import as unresolved when the venv is not activated
- `scripts/build_docs.py` refuses to mirror a site that is missing `llms.txt`, `llms-full.txt`, `skill.md`, the `.well-known/agent-skills` files, `robots.txt`, or `sitemap.xml`, since Great Docs reports success even when it skips them


### Documentation

- New user guide at https://mkennedy.codes/docs/listmonk/user-guide/getting-started.html, ten pages in sidebar order: getting started, errors and troubleshooting, subscribers, lists and segmentation, transactional email, campaigns, templates, recipes (signup form, unsubscribe link, receipt with PDF, password reset, user sync, newsletter, health check), testing your integration, and how it works. Every page is folded into `llms-full.txt`
- The README usage section is now a guided tour that follows one subscriber from signup to deletion, with every code sample unchanged
- Replaced the generated agent skill with a hand-written `skills/listmonk/SKILL.md` (wired through `skill.file` in `great-docs.yml`) that covers the rules of the package: call order, the raises-versus-returns-False error model, transactional subscriber modes, campaign status transitions, Go template syntax, and the permission behind the 403. `skill_extra_body.md` and the gotcha/decision-table lists in `great-docs.yml` folded into it
- Corrected the [test_campaign()](reference/test_campaign.html#listmonk.test_campaign) docs: Listmonk answers HTTP 400 "No known subscribers to test." when none of the addresses are subscribers, which the client raises as `httpx2.HTTPStatusError`; it does not silently send nothing. A test pins the behaviour
- README: documented [test_campaign()](reference/test_campaign.html#listmonk.test_campaign), `start/pause/cancel_campaign()`, `subscriber_mode`, and multi-recipient transactional sends, which had only been in the changelog; added an Error handling section (what raises, what returns `False` or `None`, timeouts) and FAQ entries for [OperationNotAllowedError](reference/errors.OperationNotAllowedError.html#listmonk.errors.OperationNotAllowedError) and the campaign-test 400; switched the media example to an image, which is all a default server accepts
- Every public function, model, and exception now has an Examples section, so the reference pages and `llms-full.txt` show canonical usage; [update_campaign()](reference/update_campaign.html#listmonk.update_campaign) notes that dropping a past `send_at` returns a scheduled campaign to draft
- Package docstring lists the entry points (functions, `models`, `errors`, `timeout_config`, `SSL_CERT_FILE`/`SSL_CERT_DIR`); changelog compare links added for 0.5.31 and 0.6.32

**Full changelog:** [https://github.com/mikeckennedy/listmonk/compare/v0.6.32…v0.7.33](https://github.com/mikeckennedy/listmonk/compare/v0.6.32...v0.7.33)


# v0.6.32

*2026-10-18* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.6.32)


## \[0.6.32\] - 2026-10-17


### Added

- `subscriber_mode` support in [send_transactional_email()](reference/send_transactional_email.html#listmonk.send_transactional_email): pass `'external'` to email people who are not subscribers (no more creating a temporary subscriber, sending, then deleting it) or `'fallback'` to look the recipient up but send anyway if they aren't found. The field is omitted when unset, so requests to older servers are unchanged. In these modes only `{ .Subscriber.Email }` is populated, so pass anything else the template needs via `template_data` and read it as `{ .Tx.Data.* }`. Thank you [\[<span class="citation" data-cites="waza-ari">@waza-ari</span>\](https://github.com/waza-ari)](https://github.com/waza-ari)
- [send_transactional_email()](reference/send_transactional_email.html#listmonk.send_transactional_email) now takes a list of addresses as its first argument to reach several recipients in one call, e.g. `send_transactional_email(['a@x.com', 'b@x.com'], template_id=3)`. A single string still maps to the server's `subscriber_email` field and a list to `subscriber_emails`, so the two fields the API rejects together cannot both be sent. Thank you [\[<span class="citation" data-cites="waza-ari">@waza-ari</span>\](https://github.com/waza-ari)](https://github.com/waza-ari)


# v0.5.31

*2026-07-31* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.5.31)


## \[0.5.31\] - 2026-07-31


### Added

- Type checking with [ty](https://github.com/astral-sh/ty) as the authoritative checker: a `ty.toml` config, a `ty` dev dependency, and `tests/test_type_check.py`, which fails the suite on any diagnostic (and skips when ty isn't installed). The tree is at zero diagnostics, checked against Python 3.10 -- the floor of the supported range -- so nothing newer than 3.10 slips into the public API


### Fixed

- Fixed the type errors and removed the 13 stale `# type: ignore` comments that `ty check` reported. Two were real latent crashes in `example_client/client.py`, which used a subscriber and its UUID without checking either for `None`; the example now guards once, up front, instead of suppressing the warnings


# v0.4.2

*2026-06-10* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.4.2)


## \[0.4.2\] - 2026-06-09


### Added

- Add media upload and campaign attachment support: new [upload_media()](reference/upload_media.html#listmonk.upload_media) function and [Media](reference/models.Media.html#listmonk.models.Media) model, plus a `media_ids` parameter on [create_campaign()](reference/create_campaign.html#listmonk.create_campaign) and [update_campaign()](reference/update_campaign.html#listmonk.update_campaign). Updates preserve a campaign's existing attachments unless `media_ids` is passed explicitly. (fixes [\#16](https://github.com/mikeckennedy/listmonk/issues/16))
- Documentation site at https://mkennedy.codes/docs/listmonk/ generated from the docstrings with Great Docs
- Ship a `py.typed` marker (and the `Typing :: Typed` classifier) so mypy/pyright type-check against the library's annotations
- [create_list()](reference/create_list.html#listmonk.create_list), [update_list()](reference/update_list.html#listmonk.update_list), and [delete_list()](reference/delete_list.html#listmonk.delete_list) now accept the optional `timeout_config` parameter like every other network call ([delete_list()](reference/delete_list.html#listmonk.delete_list) previously hardcoded a 30-second timeout; all three now default to 10 seconds)


### Changed

- Import `httpx2` directly instead of aliasing it as `httpx`, so signatures, docstrings, and the docs site all show `httpx2.Timeout` / `httpx2.HTTPStatusError` -- the names users actually import
- Tighten public signatures to match documented behavior: required parameters are no longer `Optional` (`create_campaign(name, subject)`, `create_template(name, body)`, `delete_campaign(campaign_id)`, `delete_template(template_id)`, `set_default_template(template_id)`, `confirm_optin(...)`), and functions that can never return `None` no longer claim `Optional` returns ([list_by_id](reference/list_by_id.html#listmonk.list_by_id), [campaign_preview_by_id](reference/campaign_preview_by_id.html#listmonk.campaign_preview_by_id), [template_preview_by_id](reference/template_preview_by_id.html#listmonk.template_preview_by_id), [create_campaign](reference/create_campaign.html#listmonk.create_campaign), [create_template](reference/create_template.html#listmonk.create_template), [create_list](reference/create_list.html#listmonk.create_list), [update_list](reference/update_list.html#listmonk.update_list))
- Fix the `headers` parameter annotation on [create_campaign()](reference/create_campaign.html#listmonk.create_campaign) -- it is a list of single-entry dicts, not a dict
- Accuracy pass over docstrings, the README, and the example client (corrected TLS/certifi guidance, README samples that would not run as written, stale claims about unimplemented list/template APIs)


### Fixed

- Fix [update_list()](reference/update_list.html#listmonk.update_list) sending the list type as `list_type` instead of `type`, so changing a list's type now actually takes effect
- Fix `Subscriber.model_dump()` crashing on server-populated subscribers (list-membership dicts and a `None` `updated_at` now serialize cleanly)
- Fix the [list_by_id()](reference/list_by_id.html#listmonk.list_by_id) workaround for listmonk[\#2117](https://github.com/mikeckennedy/listmonk/issues/2117) crashing with `AttributeError` when the server returns a result set (dict access instead of attribute access)
- Fix repeat [login()](reference/login.html#listmonk.login) calls returning `True` without re-validating the new credentials against the server


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

- Add `altbody` support to [send_transactional_email()](reference/send_transactional_email.html#listmonk.send_transactional_email) for multipart HTML transactional emails. Thank you [<span class="citation" data-cites="neilime">@neilime</span>](https://github.com/neilime)


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

- Add [update_list](reference/update_list.html#listmonk.update_list) function (thanks [<span class="citation" data-cites="ChrisH861">@ChrisH861</span>](https://github.com/ChrisH861), PR [\#27](https://github.com/mikeckennedy/listmonk/issues/27))


# v0.3.9

*2026-01-06* · [GitHub](https://github.com/mikeckennedy/listmonk/releases/tag/v0.3.9)


## \[0.3.9\] - 2026-01-05


### Added

- Add add_subscribers_to_lists function (thanks [<span class="citation" data-cites="MochaSteve256">@MochaSteve256</span>](https://github.com/MochaSteve256))


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

Thanks [<span class="citation" data-cites="neilime">@neilime</span>](https://github.com/neilime) and [<span class="citation" data-cites="obrizan">@obrizan</span>](https://github.com/obrizan) for the PRs.


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

Thank you [<span class="citation" data-cites="pastorhudson">@pastorhudson</span>](https://github.com/pastorhudson) for the PRs.


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
