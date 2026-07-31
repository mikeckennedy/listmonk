---
name: listmonk
description: >
  Listmonk Email API Client for Python. Use when writing Python code that uses the listmonk package.
license: MIT
compatibility: Requires Python >=3.10.
---

# Listmonk

Listmonk Email API Client for Python

## Installation

```bash
pip install listmonk
```

## When to use what

| Need | Use |
|------|-----|
| Look up a single subscriber | `subscriber_by_email(email) / subscriber_by_id(id) / subscriber_by_uuid(uuid)` |
| Filter subscribers by a custom attribute | `subscribers(query_text="subscribers.attribs->>'city' = 'Portland'")` |
| Unsubscribe someone but keep their record | `block_subscriber(subscriber)` |
| Erase a subscriber entirely | `delete_subscriber(email)` |
| Send a one-off email (reset code, receipt) | `send_transactional_email(email, tx_template_id, template_data={...})` |
| Attach a file to a campaign | `upload_media(path) then create_campaign(..., media_ids=[m.id])` |
| Schedule a campaign for later | `create_campaign(..., send_at=datetime.now() + timedelta(hours=1))` |
| Send a test copy of a campaign to yourself | `test_campaign(campaign_id, ['you@example.com'])` |
| Actually send a draft campaign | `start_campaign(campaign_id) — or set_campaign_status(id, CampaignStatuses.running)` |
| Stop a campaign that is sending | `pause_campaign(campaign_id) to resume later, cancel_campaign(campaign_id) to stop for good` |

## API overview

### Configuration & Authentication

Point the client at your Listmonk instance and authenticate.

- `set_url_base`: Set the base URL of your Listmonk instance for all subsequent calls
- `get_base_url`: Return the configured base URL of your Listmonk instance
- `login`: Log into Listmonk and cache the credentials for the life of your app
- `verify_login`: Verify that the stored login credentials are still valid at the server
- `is_healthy`: Check whether the server is reachable and the stored credentials are valid

### Mailing Lists

Read and manage mailing lists.

- `lists`: Get all mailing lists on the server
- `list_by_id`: Get the full details of a single mailing list by its ID
- `create_list`: Create a new mailing list on the server
- `update_list`: Update an existing mailing list on the server
- `delete_list`: Delete a mailing list by its ID

### Subscribers

Create, query, update, and manage the status of subscribers.

- `subscribers`: Get the list of subscribers matching the given criteria, or all subscribers if no criteria are given
- `subscriber_by_email`: Retrieve a single subscriber by their email address (e.g. "some_user@talkpython.fm")
- `subscriber_by_id`: Retrieve a single subscriber by their numeric Listmonk ID (e.g. 201)
- `subscriber_by_uuid`: Retrieve a single subscriber by their UUID (e.g. "c37786af-e6ab-4260-9b49-740adpcm6ed")
- `create_subscriber`: Create a new subscriber on the Listmonk server
- `update_subscriber`: Update many aspects of a subscriber: email and name, custom attribute data, list membership, and status
- `add_subscribers_to_lists`: Add a number of subscribers to a number of lists in a single bulk operation
- `enable_subscriber`: Set a subscriber's status to enabled so they will receive campaigns
- `disable_subscriber`: Set a subscriber's status to disabled, pausing their subscription so they will not receive campaigns
- `block_subscriber`: Add a subscriber to the blocklist, effectively unsubscribing them so they will not receive any mail
- `confirm_optin`: Confirm a subscriber's opt-in to a list via the API
- `delete_subscriber`: Completely delete a subscriber from your system (as if they were never there)

### Campaigns

Create, preview, update, test, send, and delete email campaigns.

- `campaigns`: Get all campaigns on the server
- `campaign_by_id`: Get the full details of a campaign with the given ID
- `campaign_preview_by_id`: Get the rendered preview of a campaign with the given ID
- `create_campaign`: Create a new campaign with the given parameters
- `update_campaign`: Update an existing campaign with the provided campaign information
- `test_campaign`: Send a one-off test copy of a campaign to specific addresses
- `set_campaign_status`: Move a campaign to a new lifecycle status
- `start_campaign`: Start sending a campaign
- `pause_campaign`: Pause a campaign that is currently sending
- `cancel_campaign`: Stop a campaign for good
- `delete_campaign`: Completely delete a campaign from your system

### Media

Upload files to the media library to attach to campaigns.

- `upload_media`: Upload a file to the Listmonk media library

### Templates

Manage email templates and set the default.

- `templates`: Retrieve all templates defined on the Listmonk instance
- `template_by_id`: Retrieve a single template by its numeric ID
- `template_preview_by_id`: Render and return a preview of a template
- `create_template`: Create a new template on the Listmonk instance
- `update_template`: Update an existing template on the Listmonk instance
- `set_default_template`: Mark the given template as the default for its type
- `delete_template`: Permanently delete a template from the Listmonk instance

### Transactional Email

Send one-off transactional messages.

- `send_transactional_email`: Send a transactional email through Listmonk to a single recipient

### Data Models

Pydantic models returned by and passed to the API functions.

- `models.MailingList`
- `models.SubscriberStatus`
- `models.SubscriberStatuses`
- `models.Subscriber`
- `models.CreateSubscriberModel`
- `models.Campaign`
- `models.CampaignStatuses`
- `models.CreateCampaignModel`
- `models.UpdateCampaignModel`
- `models.CampaignPreview`
- `models.Template`
- `models.CreateTemplateModel`
- `models.TemplatePreview`
- `models.Media`

### Exceptions

Errors raised by the client.

- `errors.ValidationError`
- `errors.OperationNotAllowedError`
- `errors.ListmonkFileNotFoundError`

## Gotchas

1. Call set_url_base() then login() before any other function, or every data call raises OperationNotAllowedError.
2. login(), is_healthy(), and verify_login() return False (they do not raise) when credentials are rejected or the server is unreachable — check the bool.
3. Timeouts use httpx2 (a fork of httpx), not httpx: build them with httpx2.Timeout(...) and catch httpx2.HTTPStatusError.
4. Every template body must contain the Go-template placeholder {{ template "content" . }} exactly once, or create_template() raises ValueError. It is Go template syntax, not Jinja.
5. update_campaign() replaces the whole attachment set: media_ids=None re-sends the campaign's existing media, media_ids=[] clears them, and a new list swaps them. A past send_at is silently dropped to None.
6. update_campaign() cannot change a campaign's status — Listmonk ignores `status` on PUT /api/campaigns/{id}. Use set_campaign_status() (or start/pause/cancel_campaign()), which calls the dedicated /status endpoint.
7. test_campaign() only delivers to addresses that already exist as subscribers; Listmonk will not create them, and a test to an unknown address silently sends nothing.
8. subscribers(query_text=...) requires the subscribers:sql_query permission on the user's role, or the server returns HTTP 403.
9. send_transactional_email() requires the recipient to already be a subscriber, and template_id must reference a 'tx' template, not a 'campaign' template.
10. Auth is module-level global state: only one instance can be targeted at a time and credential changes are not thread-safe.
11. Custom email headers are a list of single-entry dicts (e.g. [{'X-Priority': '1'}]), not one dict.

## Best practices

- Configure set_url_base() then login() once at startup and check login()'s bool return before proceeding.
- Update objects by fetching the model, mutating fields in place, then passing it back to update_subscriber/update_campaign/update_template — the client re-fetches and returns the server's fresh copy.
- Use block_subscriber() to unsubscribe someone while keeping their record; use delete_subscriber() to erase them entirely.
- Attach files to a campaign with upload_media() then media_ids=[...]; attach to a transactional email inline via attachments=[Path(...)].
- Preview a campaign with campaign_preview_by_id(), then test_campaign(id, ['you@example.com']) to a real inbox, before start_campaign() sends it to the lists.
- Pass the models.CampaignStatuses enum to set_campaign_status() rather than a raw string — an unrecognized status reaches Postgres and comes back as an opaque HTTP 500.
- Pass a custom httpx2.Timeout via timeout_config for slow or self-hosted instances (the default is 10 seconds).

## End-to-end wiring

`listmonk` is a flat module with global auth state, not a client object. Configure the base URL, log in once, then call functions directly. `set_url_base()` must come before everything, and `login()` returns a bool (it does not raise on bad credentials) — check it.

```python
import listmonk

listmonk.set_url_base('https://listmonk.yourdomain.com')  # scheme required; no /api path
if not listmonk.login('admin', 'super-secret'):           # False = rejected OR unreachable
    raise SystemExit('Login failed: check credentials and base URL.')

# Add someone, then send them a transactional email.
sub = listmonk.create_subscriber('user@example.com', 'Jane Doe', list_ids={1}, pre_confirm=True)
listmonk.send_transactional_email('user@example.com', template_id=3, template_data={'name': 'Jane'})
```

Because auth is module-level global state, only one Listmonk instance can be targeted at a time and credential changes are not thread-safe. Every data call runs an internal state check and raises `OperationNotAllowedError` if the base URL is unset or you have not logged in.

## Two error models: raises vs. returns False

This trips people up. Some functions raise on failure; others report failure through their return value. Do not wrap the "returns False" ones in `try/except` expecting an exception.

- **Return `False` (never raise on failure):** `login()`, `is_healthy()`, `verify_login()` (rejected creds / unreachable), `confirm_optin()` (non-2xx status), `add_subscribers_to_lists()` (empty inputs or error status).
- **Return `None` when nothing matches:** `subscriber_by_email()`, `subscriber_by_id()`, `subscriber_by_uuid()`, `campaign_by_id()`, `template_by_id()`, and `set_campaign_status()` / `start_campaign()` / `pause_campaign()` / `cancel_campaign()` for an unknown campaign ID. `test_campaign()` returns `False` in that same case.
- **Raise:** most create/update/delete calls raise `ValueError` for bad arguments, `httpx2.HTTPStatusError` on 4xx/5xx, and `ValidationError` on an empty/malformed server body. `list_by_id()` returns a `MailingList` (not `Optional`) and raises if the ID is missing.

Note `httpx2` (a fork of `httpx` with a near-identical API), not `httpx`: catch `httpx2.HTTPStatusError` and build timeouts with `httpx2.Timeout(timeout=30.0)`.

## The mutate-then-pass-back update pattern

`update_subscriber`, `update_campaign`, and `update_template` take the model object, not loose fields. Fetch it, mutate attributes in place, pass it back — the client sends the full record and re-fetches the server's fresh copy as the return value.

```python
sub = listmonk.subscriber_by_email('user@example.com')
sub.name = 'Updated Name'
sub.attribs['rating'] = 7
# List membership: existing lists - remove_from_lists + add_to_lists
updated = listmonk.update_subscriber(sub, add_to_lists={4}, remove_from_lists={5})
```

`update_subscriber(status=...)` can enable/disable/block, but for status-only changes prefer the dedicated wrappers: `enable_subscriber(sub)`, `disable_subscriber(sub)`, `block_subscriber(sub)`. Use `block_subscriber` to unsubscribe someone while keeping their record; use `delete_subscriber(email)` to erase them entirely.

## Subscriber querying (Listmonk SQL-ish syntax)

`subscribers(query_text=...)` passes a server-side SQL-like filter over the `subscribers` table. Custom attributes are queried through the JSONB `->>` operator. This requires the `subscribers:sql_query` permission on the user's role or the server returns 403.

```python
listmonk.subscribers(query_text="subscribers.email = 'user@example.com'")
listmonk.subscribers(query_text="subscribers.attribs->>'city' = 'Portland'")
listmonk.subscribers(list_id=3)  # list filter needs no permission
```

## Templates use Go template syntax (not Jinja)

Listmonk renders templates with Go's `text/template`/`html/template`, so the syntax is `{{ ... }}` with a leading dot for context — **not** Jinja/Django. Every template body **must** contain the placeholder `{{ template "content" . }}` exactly once, or `create_template()` raises `ValueError` before any request is sent.

```python
# Campaign body pulls subscriber fields from .Subscriber
body = '<html><body>Hi {{ .Subscriber.FirstName }}! {{ template "content" . }}</body></html>'
listmonk.create_template(name='Welcome', body=body, type='campaign')
```

There are two template types: `'campaign'` and `'tx'` (transactional). Merge data you pass to `send_transactional_email(template_data=...)` is available in a `tx` template as `{{ .Tx.Data.<key> }}`; subscriber fields are `{{ .Subscriber.<Field> }}`.

## Media vs. transactional attachments — two different mechanisms

Attaching a file to a **campaign** is a two-step flow: upload to the media library, then reference the returned `id`. Attaching to a **transactional** email is inline via `Path` objects — no upload step.

```python
from pathlib import Path

# Campaign attachment: upload_media() -> media_ids
media = listmonk.upload_media(Path('/path/to/report.png'))        # or bytes + filename=
listmonk.create_campaign(name='Report', subject='This month', media_ids=[media.id])

# Transactional attachment: pass Paths directly
listmonk.send_transactional_email('user@example.com', template_id=3,
                                  attachments=[Path('/path/to/invoice.pdf')])
```

`update_campaign` replaces the whole attachment set each call: with `media_ids=None` it re-sends the campaign's existing media, `media_ids=[]` clears them, and a new list swaps them. It also silently drops a `send_at` that is already in the past so a stale schedule doesn't fail the update. The default Listmonk server only allows image extensions in the media library, and there's no delete-media endpoint in this client.

## Testing and sending a campaign

Creating a campaign does not send it. A campaign starts as a `draft` and only begins delivering once its status becomes `running`, which is a **separate endpoint** — `update_campaign` ignores `status`.

```python
from listmonk.models import CampaignStatuses

campaign = listmonk.create_campaign(name='June', subject='Our June Update', body='# Hi')

# Send a test copy first. Each address must already be a subscriber; the campaign
# stays a draft and its stats are untouched.
listmonk.test_campaign(campaign.id, ['you@example.com'])  # -> True

listmonk.start_campaign(campaign.id)   # or set_campaign_status(id, CampaignStatuses.running)
listmonk.pause_campaign(campaign.id)   # halt, resumable with start_campaign()
listmonk.cancel_campaign(campaign.id)  # stop for good
```

`start_campaign`, `pause_campaign`, and `cancel_campaign` are thin wrappers over `set_campaign_status(campaign_id, status)`; reach for `set_campaign_status` directly for the other members of `CampaignStatuses` (`draft`, `scheduled`, `finished`). All of them return the updated `Campaign`, or `None` if no campaign has that ID. Prefer the enum over a raw string: an unrecognized status reaches Postgres and surfaces as an opaque HTTP 500. A rejected but valid transition (starting an already-finished campaign, say) raises `httpx2.HTTPStatusError`.

## Scheduling and content types

`create_campaign(send_at=datetime.now() + timedelta(hours=1))` schedules a send. `content_type` is `'richtext' | 'html' | 'markdown' | 'plain'` for campaigns; transactional email uses `'html' | 'markdown' | 'plain'` and defaults to `'markdown'`. Custom email headers are a **list of single-entry dicts** (e.g. `[{'X-Priority': '1'}]`), not a single dict.

## Fetching the docs as Markdown

Every page on the documentation site has a plain-Markdown twin: swap the `.html` extension for `.md` to get token-efficient source without the site chrome. For example https://mkennedy.codes/docs/listmonk/reference/subscribers.html is also available at https://mkennedy.codes/docs/listmonk/reference/subscribers.md. Prefer the `.md` form when reading these docs programmatically.
</content>


## Resources

- [Full documentation](https://mkennedy.codes/docs/listmonk/)
- [llms.txt](llms.txt) — Indexed API reference for LLMs
- [llms-full.txt](llms-full.txt) — Comprehensive documentation for LLMs
- [Source code](https://github.com/mikeckennedy/listmonk)
