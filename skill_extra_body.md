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
