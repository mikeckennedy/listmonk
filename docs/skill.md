---
name: listmonk
description: >
  Python client for a self-hosted Listmonk email server: subscribers, mailing lists, campaigns, templates, media, and transactional email, built on httpx2 and Pydantic. Use when adding listmonk to a Python app, writing code that calls listmonk.* functions, choosing between transactional subscriber modes or campaign status calls, or when a call raises OperationNotAllowedError, httpx2.HTTPStatusError (403 Forbidden, 400 No known subscribers to test), or listmonk.errors.ValidationError.
license: MIT
compatibility: Requires Python >=3.10 and a reachable Listmonk instance with an API user.
---

# listmonk

`listmonk` wraps the subset of the Listmonk REST API that web apps need: subscribe and unsubscribe people, segment them into lists, send transactional email, and create, test, and send campaigns. It is a flat module with module-level auth state, not a client object. Failures come back three ways: `listmonk.errors.OperationNotAllowedError` when the client is not configured, `httpx2.HTTPStatusError` for any 4xx or 5xx response, and `listmonk.errors.ValidationError` for bad arguments or a non-JSON body. Several calls report failure by returning `False` or `None` instead of raising (see Rules).

## Install

`pip install listmonk` or `uv add listmonk`.

## Use

```python
import listmonk

listmonk.set_url_base('https://listmonk.your.domain')  # scheme required, no /api path; must come first
if not listmonk.login('api_user', 'token'):            # False means rejected OR unreachable; it does not raise
    raise SystemExit('Listmonk login failed')

sub = listmonk.create_subscriber('user@example.com', 'Jane Doe', list_ids={1}, pre_confirm=True)
listmonk.send_transactional_email('user@example.com', template_id=3, template_data={'name': 'Jane'})
```

In a test suite, patch the module-level `httpx2.get`, `httpx2.post`, `httpx2.put`, and `httpx2.delete` with a fake that returns `httpx2.Response` objects; the library calls those verbs directly, so there is no client to inject. Set `listmonk.impl.has_logged_in = True` and `listmonk.impl.url_base` in a fixture to skip the login round trip. In CI, keep real credentials out of the suite: the package's own tests run entirely against an in-memory fake.

## Rules

- Call `set_url_base()` then `login()` before anything else. Every other call raises `OperationNotAllowedError` until a login has succeeded. A second `login()` re-validates the new credentials against the server; it does not short-circuit.
- `login()`, `is_healthy()`, and `verify_login()` return `False` instead of raising when credentials are rejected or the server is unreachable. Check the bool.
- Lookups return `None` when nothing matches: `subscriber_by_email/id/uuid()`, `campaign_by_id()`, `template_by_id()`, and `set_campaign_status()` plus its `start/pause/cancel_campaign()` wrappers for an unknown campaign ID. `delete_subscriber()`, `delete_campaign()`, `delete_template()`, and `test_campaign()` return `False` for an unknown target. `list_by_id()` is the exception: it raises for a missing ID.
- `confirm_optin()` and `add_subscribers_to_lists()` return `False` on a non-2xx response; they never raise for HTTP errors.
- The HTTP library is `httpx2`, a fork of httpx. Catch `httpx2.HTTPStatusError` and build timeouts with `httpx2.Timeout(timeout=30)`, passed as `timeout_config=` to any call. The default is 10 seconds.
- `subscribers(query_text=...)`, `subscriber_by_email()`, and `subscriber_by_uuid()` send a server-side SQL filter, so the API user's role needs the `subscribers:sql_query` permission or the server returns 403. `subscriber_by_id()` and `subscribers(list_id=...)` do not need it.
- Templates use Go template syntax (`{{ .Subscriber.Email }}`, `{{ .Tx.Data.key }}`), not Jinja. Every template body must contain `{{ template "content" . }}` or `create_template()` raises `ValueError` before sending anything. `update_template()` does not validate the placeholder.
- `send_transactional_email()` needs a `tx` template ID, not a campaign template. By default the recipient must already be a subscriber. `subscriber_mode='external'` sends to anyone without a lookup; `'fallback'` looks up first and sends anyway if not found. In both modes only `{{ .Subscriber.Email }}` is populated, so pass everything else through `template_data`. Omit `subscriber_mode` and the field is left off the request, which keeps older servers working.
- A single address is sent as `subscriber_email` and a list as `subscriber_emails`. The server rejects a request that carries both, which the one-parameter design makes impossible to express.
- Campaign attachments are two steps: `upload_media()` then `media_ids=[media.id]`. Transactional attachments are inline `Path` objects. `update_campaign()` re-sends the campaign's current media when `media_ids=None`, clears them with `media_ids=[]`, and replaces them with a new list.
- `update_campaign()` cannot change status; Listmonk ignores it on that endpoint. Use `set_campaign_status()` or `start/pause/cancel_campaign()`. A `send_at` already in the past is silently dropped on update, and Listmonk then moves a `scheduled` campaign back to `draft`.
- Creating a campaign does not send it. The order is `campaign_preview_by_id()`, `test_campaign()`, then `start_campaign()`. Test addresses must already be subscribers: when none are known the server answers 400 "No known subscribers to test." and the client raises `httpx2.HTTPStatusError`.
- Pass the `models.CampaignStatuses` enum to `set_campaign_status()`. An unknown string reaches Postgres and comes back as an opaque HTTP 500. Valid transitions are draft to scheduled or running, scheduled to draft, running to paused or cancelled, paused to running; anything else is a 400.
- Custom email headers are a list of single-entry dicts, `[{'X-Priority': '1'}]`, never one dict.
- `create_subscriber()` lowercases and strips the email and always creates the subscriber as `enabled`. `update_subscriber()` sends the whole record, recomputes list membership as existing minus `remove_from_lists` plus `add_to_lists`, preconfirms those subscriptions, and keeps the subscriber's current status unless you pass `status=`.
- Auth is module-level global state: one Listmonk instance per process, and credential changes are not thread-safe.

## Decision table

| Need | Use |
| ---- | --- |
| Look up one subscriber | `subscriber_by_email(email)`, `subscriber_by_id(id)`, `subscriber_by_uuid(uuid)` |
| Filter subscribers by a custom attribute | `subscribers(query_text="subscribers.attribs->>'city' = 'Portland'")` |
| Unsubscribe but keep the record | `block_subscriber(sub)`; `disable_subscriber(sub)` to pause instead |
| Erase a subscriber | `delete_subscriber(email)` or `delete_subscriber(overriding_subscriber_id=id)` |
| Put existing subscribers on lists in bulk | `add_subscribers_to_lists([ids], [list_ids])` |
| Confirm a double opt-in from your own form | `confirm_optin(sub.uuid, lst.uuid)` |
| Send a one-off email to a subscriber | `send_transactional_email(email, tx_template_id, template_data={...})` |
| Email someone who is not a subscriber | `send_transactional_email(email, tx_template_id, subscriber_mode='external', template_data={...})` |
| One transactional email to several people | `send_transactional_email(['a@x.com', 'b@x.com'], tx_template_id)` |
| Attach a file to a campaign | `upload_media(path)` then `create_campaign(..., media_ids=[media.id])` |
| Schedule a campaign | `create_campaign(..., send_at=datetime.now() + timedelta(hours=1))` |
| Send a test copy to yourself | `test_campaign(campaign_id, ['you@example.com'])` |
| Send a draft campaign | `start_campaign(campaign_id)` |
| Stop a sending campaign | `pause_campaign(id)` to resume later, `cancel_campaign(id)` for good |
| Slow or self-hosted server | `timeout_config=httpx2.Timeout(timeout=60)` on any call |
| Corporate CA on the server | `SSL_CERT_FILE=/path/ca.pem` or `SSL_CERT_DIR=` in the environment |

## API

- `set_url_base(url) -> None`, `get_base_url() -> str | None`. Raises `ValidationError` without an http(s) scheme.
- `login(user_name, pw, timeout_config=None) -> bool`, `verify_login() -> bool`, `is_healthy() -> bool`. Never raise on bad credentials.
- `lists() -> list[MailingList]`, `list_by_id(list_id) -> MailingList`, `create_list(list_name, list_type='public', optin='single', tags=None, description=None)`, `update_list(list_id, list_name=None, list_type=None, status=None, optin=None, tags=None, description=None)`, `delete_list(list_id) -> bool`. Only the fields you pass to `update_list()` change.
- `subscribers(query_text=None, list_id=None) -> list[Subscriber]` (pages through 500 at a time), `subscriber_by_email(email)`, `subscriber_by_id(id)`, `subscriber_by_uuid(uuid)` -> `Subscriber | None`.
- `create_subscriber(email, name=None, list_ids=None, pre_confirm=False, attribs=None) -> Subscriber`. A duplicate email is an HTTP 409 from the server.
- `update_subscriber(sub, add_to_lists=None, remove_from_lists=None, status=None) -> Subscriber | None`, plus `enable_subscriber(sub)`, `disable_subscriber(sub)`, `block_subscriber(sub)`. Mutate the model, pass it back, use the returned fresh copy.
- `add_subscribers_to_lists(subscriber_ids, list_ids, status='confirmed') -> bool`, `confirm_optin(subscriber_uuid, list_uuid) -> bool`, `delete_subscriber(email=None, overriding_subscriber_id=None) -> bool`.
- `send_transactional_email(subscriber_email: str | list[str], template_id, from_email=None, template_data=None, messenger_channel='email', content_type='markdown', altbody=None, attachments=None, email_headers=None, subscriber_mode=None) -> bool`. Raises `ListmonkFileNotFoundError` for a missing attachment.
- `upload_media(file: Path | bytes, filename=None) -> Media`. `filename` is required for bytes. A default server only accepts image extensions.
- `campaigns() -> list[Campaign]`, `campaign_by_id(id) -> Campaign | None`, `campaign_preview_by_id(id) -> CampaignPreview`, `create_campaign(name, subject, list_ids={1}, from_email=None, campaign_type=None, content_type=None, body=None, alt_body=None, send_at=None, messenger=None, template_id=None, tags=None, headers=None, media_ids=None) -> Campaign`, `update_campaign(campaign, media_ids=None) -> Campaign | None`, `delete_campaign(id) -> bool`. `template_id=None` means the server's default template.
- `test_campaign(campaign_id, emails) -> bool`, `set_campaign_status(campaign_id, status: CampaignStatuses) -> Campaign | None`, `start_campaign(id)`, `pause_campaign(id)`, `cancel_campaign(id)`.
- `templates() -> list[Template]`, `template_by_id(id) -> Template | None`, `template_preview_by_id(id) -> TemplatePreview`, `create_template(name, body, type=None, is_default=None, subject=None) -> Template` (`type` is `'campaign'` or `'tx'`), `update_template(template) -> Template | None` (does not touch `is_default`), `set_default_template(id) -> bool`, `delete_template(id) -> bool`.
- `models`: `MailingList`, `Subscriber`, `Campaign`, `Template`, `Media`, the enums `SubscriberStatuses` and `CampaignStatuses`, and the request payloads `CreateSubscriberModel`, `CreateCampaignModel`, `UpdateCampaignModel`, `CreateTemplateModel`. `errors`: `ValidationError`, `OperationNotAllowedError` (a `ValidationError` subclass), `ListmonkFileNotFoundError` (a `FileNotFoundError` subclass).

## Reading a failure

```text
httpx2.HTTPStatusError: Client error '403 Forbidden' for url 'https://lm.example/api/subscribers?page=1&per_page=100&query=subscribers.email='jo@x.com''
```

The `query=` in the URL means a SQL-filtered lookup, so the 403 is the missing `subscribers:sql_query` permission on the API user's role, not a bad password (a bad password makes `login()` return `False` earlier). Fix order: confirm `login()` returned `True`, then fix the role in Listmonk's Users and Roles screen, then retry. `OperationNotAllowedError: URL Base must be set to proceed.` or `You must login before proceeding.` means the configuration calls were skipped or ran in another process.

## Resources

- Documentation: <https://mkennedy.codes/docs/listmonk/>
- API reference: <https://mkennedy.codes/docs/listmonk/reference/> (append `.md` instead of `.html` to any page for plain Markdown)
- User guide: <https://mkennedy.codes/docs/listmonk/user-guide/getting-started.html> (getting started, subscribers, lists, transactional email, campaigns, templates, recipes, testing, how it works)
- Errors and troubleshooting: <https://mkennedy.codes/docs/listmonk/user-guide/error-handling.html>
- Recipes (signup form, unsubscribe link, receipt with PDF, user sync, newsletter): <https://mkennedy.codes/docs/listmonk/user-guide/recipes.html>
- llms.txt: <https://mkennedy.codes/docs/listmonk/llms.txt>
- llms-full.txt: <https://mkennedy.codes/docs/listmonk/llms-full.txt>
- Source: <https://github.com/mikeckennedy/listmonk>
- Listmonk server API docs: <https://listmonk.app/docs/apis/apis/>
