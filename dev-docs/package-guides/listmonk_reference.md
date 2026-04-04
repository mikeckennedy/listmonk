# listmonk — Comprehensive API Reference

> Python client library for the open-source, self-hosted [Listmonk](https://listmonk.app) email platform.
> Built on [httpx](https://www.python-httpx.org) and [Pydantic](https://pydantic.dev). Supports Python 3.10+.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Authentication](#authentication)
- [Health Check](#health-check)
- [Subscribers](#subscribers)
- [Lists](#lists)
- [Campaigns](#campaigns)
- [Templates](#templates)
- [Transactional Email](#transactional-email)
- [Models Reference](#models-reference)
- [Errors](#errors)
- [API Endpoints](#api-endpoints)
- [FAQ / Troubleshooting](#faq--troubleshooting)
- [Complete Public API](#complete-public-api)

---

## Installation

```bash
pip install listmonk
```

Dependencies: `httpx`, `pydantic`, `strenum`

---

## Quick Start

```python
import listmonk

# 1. Point at your Listmonk instance
listmonk.set_url_base('https://listmonk.yourdomain.com')

# 2. Authenticate
listmonk.login('your_username', 'your_password')

# 3. Use the API
subscribers = listmonk.subscribers(list_id=3)
for sub in subscribers:
    print(sub.email, sub.name)
```

---

## Configuration

### `set_url_base(url: str) -> None`

Set the base URL of your Listmonk instance. Must be called before any other operation.

```python
listmonk.set_url_base('https://listmonk.yourdomain.com')
```

- URL must start with `http://` or `https://`
- Trailing slashes are stripped automatically
- Do **not** include `/api` — the library appends that

Raises `ValidationError` if URL is empty or missing scheme.

### `get_base_url() -> Optional[str]`

Returns the currently configured base URL, or `None` if not set.

```python
url = listmonk.get_base_url()
```

---

## Authentication

The library uses HTTP Basic Auth. Credentials are stored globally for the lifetime of your application.

### `login(user_name: str, pw: str, timeout_config: Optional[httpx.Timeout] = None) -> bool`

Authenticate with your Listmonk instance. Must call `set_url_base()` first.

```python
success = listmonk.login('admin', 'secretpassword')
```

- Validates credentials against the server immediately
- Returns `True` if authentication succeeded, `False` otherwise
- Raises `OperationNotAllowedError` if `set_url_base()` has not been called
- Raises `ValidationError` if username or password is empty

### `verify_login(timeout_config: Optional[httpx.Timeout] = None) -> bool`

Verify that stored credentials are still valid.

```python
still_valid = listmonk.verify_login()
```

---

## Health Check

### `is_healthy(timeout_config: Optional[httpx.Timeout] = None) -> bool`

Check if the Listmonk instance is alive and accessible with current credentials.

```python
if listmonk.is_healthy():
    print('Listmonk is up!')
```

Returns `False` on any error (network, auth, etc.) rather than raising.

---

## Subscribers

### Retrieving Subscribers

#### `subscribers(query_text: Optional[str] = None, list_id: Optional[int] = None, timeout_config: Optional[httpx.Timeout] = None) -> list[Subscriber]`

Get subscribers matching criteria. Returns all subscribers if no filters provided. Handles pagination automatically (500 per page).

```python
# All subscribers
all_subs = listmonk.subscribers()

# Subscribers from a specific list
list_subs = listmonk.subscribers(list_id=3)

# SQL query filtering (Listmonk query syntax)
results = listmonk.subscribers(query_text="subscribers.email = 'user@example.com'")
results = listmonk.subscribers(query_text="subscribers.attribs->>'city' = 'Portland'")
```

See [Listmonk querying docs](https://listmonk.app/docs/querying-and-segmentation/) for full query syntax.

#### `subscriber_by_email(email: str, timeout_config: Optional[httpx.Timeout] = None) -> Optional[Subscriber]`

Look up a single subscriber by email address.

```python
sub = listmonk.subscriber_by_email('user@example.com')
if sub:
    print(f'{sub.name} (ID: {sub.id})')
```

Returns `None` if not found.

#### `subscriber_by_id(subscriber_id: int, timeout_config: Optional[httpx.Timeout] = None) -> Optional[Subscriber]`

Look up a single subscriber by their numeric ID.

```python
sub = listmonk.subscriber_by_id(2001)
```

Returns `None` if not found.

#### `subscriber_by_uuid(subscriber_uuid: str, timeout_config: Optional[httpx.Timeout] = None) -> Optional[Subscriber]`

Look up a single subscriber by their UUID.

```python
sub = listmonk.subscriber_by_uuid('f6668cf0-1c2e-...')
```

Returns `None` if not found.

### Creating Subscribers

#### `create_subscriber(email: str, name: str, list_ids: set[int], pre_confirm: bool, attribs: dict[str, Any], timeout_config: Optional[httpx.Timeout] = None) -> Subscriber`

Create a new subscriber.

```python
new_sub = listmonk.create_subscriber(
    email='user@example.com',
    name='Jane Doe',
    list_ids={1, 7, 9},
    pre_confirm=True,        # Skip double opt-in confirmation
    attribs={'city': 'Portland', 'plan': 'pro'},
)
print(f'Created with ID: {new_sub.id}')
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `email` | `str` | Subscriber's email address (required) |
| `name` | `str` | Full name, e.g. "First Last" (required) |
| `list_ids` | `set[int]` | Set of list IDs to subscribe to |
| `pre_confirm` | `bool` | If `True`, skips double opt-in email confirmation |
| `attribs` | `dict[str, Any]` | Custom attributes stored on the subscriber |

Raises `ValueError` if email or name is empty.

### Updating Subscribers

#### `update_subscriber(subscriber: Optional[Subscriber], add_to_lists: Optional[set[int]] = None, remove_from_lists: Optional[set[int]] = None, status: SubscriberStatuses = SubscriberStatuses.enabled, timeout_config: Optional[httpx.Timeout] = None) -> Optional[Subscriber]`

Update a subscriber's details, list memberships, and status.

```python
sub = listmonk.subscriber_by_email('user@example.com')

# Modify fields on the object
sub.email = 'newemail@example.com'
sub.name = 'Updated Name'
sub.attribs['rating'] = 7

# Save changes, add to list 4, remove from list 5
updated = listmonk.update_subscriber(sub, add_to_lists={4}, remove_from_lists={5})
```

The function:
1. Merges `add_to_lists` with the subscriber's existing lists
2. Removes `remove_from_lists` from the result
3. Sends the full update to the server
4. Returns the refreshed subscriber from the server

### Subscriber Status Management

#### `disable_subscriber(subscriber: Optional[Subscriber], timeout_config: Optional[httpx.Timeout] = None) -> Optional[Subscriber]`

Set a subscriber's status to "disabled".

```python
disabled = listmonk.disable_subscriber(subscriber)
```

#### `enable_subscriber(subscriber: Subscriber, timeout_config: Optional[httpx.Timeout] = None) -> Optional[Subscriber]`

Re-enable a disabled subscriber.

```python
enabled = listmonk.enable_subscriber(subscriber)
```

#### `block_subscriber(subscriber: Subscriber, timeout_config: Optional[httpx.Timeout] = None) -> Optional[Subscriber]`

Blocklist (unsubscribe) a subscriber. This is the equivalent of "unsubscribe" — they remain in the system but won't receive emails.

```python
listmonk.block_subscriber(subscriber)
```

### Deleting Subscribers

#### `delete_subscriber(email: Optional[str] = None, overriding_subscriber_id: Optional[int] = None, timeout_config: Optional[httpx.Timeout] = None) -> bool`

Permanently delete a subscriber. If you want to unsubscribe instead, use `block_subscriber`.

```python
# Delete by email
deleted = listmonk.delete_subscriber('user@example.com')

# Delete by ID (takes precedence over email)
deleted = listmonk.delete_subscriber(overriding_subscriber_id=2001)
```

Returns `True` on success, `False` if subscriber not found.

### Opt-in Confirmation

#### `confirm_optin(subscriber_uuid: Optional[str], list_uuid: Optional[str], timeout_config: Optional[httpx.Timeout] = None) -> bool`

Confirm a subscriber's opt-in for a specific list via the API (for double opt-in lists).

```python
confirmed = listmonk.confirm_optin(subscriber.uuid, mailing_list.uuid)
```

Use this when you manage opt-in confirmation on your own platform rather than through Listmonk's built-in email flow.

### Bulk List Management

#### `add_subscribers_to_lists(subscriber_ids: Iterable[int], list_ids: Iterable[int], timeout_config: Optional[httpx.Timeout] = None, status: str = 'confirmed') -> bool`

Add multiple subscribers to multiple lists in a single operation.

```python
success = listmonk.add_subscribers_to_lists(
    subscriber_ids=[101, 102, 103],
    list_ids=[5, 6],
    status='confirmed',  # or 'unconfirmed'
)
```

Returns `True` on success, `False` on failure.

---

## Lists

### `lists(timeout_config: Optional[httpx.Timeout] = None) -> list[MailingList]`

Get all mailing lists.

```python
all_lists = listmonk.lists()
for lst in all_lists:
    print(f'{lst.name}: {lst.subscriber_count} subscribers')
```

### `list_by_id(list_id: int, timeout_config: Optional[httpx.Timeout] = None) -> Optional[MailingList]`

Get a single list by ID.

```python
my_list = listmonk.list_by_id(7)
print(my_list.name, my_list.uuid)
```

### `create_list(list_name: str, list_type: str = 'public', optin: str = 'single', tags: Optional[list[str]] = None, description: Optional[str] = None) -> Optional[MailingList]`

Create a new mailing list.

```python
new_list = listmonk.create_list(
    list_name='Newsletter',
    list_type='public',     # 'public' or 'private'
    optin='single',         # 'single' or 'double'
    tags=['newsletter', 'weekly'],
    description='Our weekly newsletter',
)
```

**Parameters:**

| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| `list_name` | `str` | required | — |
| `list_type` | `str` | `'public'` | `'public'`, `'private'` |
| `optin` | `str` | `'single'` | `'single'`, `'double'` |
| `tags` | `list[str]` | `None` | — |
| `description` | `str` | `None` | — |

### `update_list(list_id: int, list_name: Optional[str] = None, list_type: Optional[str] = None, status: Optional[str] = None, optin: Optional[str] = None, tags: Optional[list[str]] = None, description: Optional[str] = None) -> Optional[MailingList]`

Update an existing list. Only provided fields are updated.

```python
updated = listmonk.update_list(
    list_id=7,
    list_name='Renamed List',
    status='archived',  # 'active' or 'archived'
)
```

### `delete_list(list_id: int) -> bool`

Delete a list by ID.

```python
deleted = listmonk.delete_list(7)
```

Returns `True` on success, `False` if list not found.

---

## Campaigns

### Retrieving Campaigns

#### `campaigns(timeout_config: Optional[httpx.Timeout] = None) -> list[Campaign]`

Get all campaigns.

```python
all_campaigns = listmonk.campaigns()
for c in all_campaigns:
    print(f'{c.name}: {c.status} ({c.sent}/{c.to_send} sent)')
```

#### `campaign_by_id(campaign_id: int, timeout_config: Optional[httpx.Timeout] = None) -> Optional[Campaign]`

Get a single campaign by ID.

```python
campaign = listmonk.campaign_by_id(15)
```

#### `campaign_preview_by_id(campaign_id: int, timeout_config: Optional[httpx.Timeout] = None) -> Optional[CampaignPreview]`

Get the rendered HTML preview of a campaign.

```python
preview = listmonk.campaign_preview_by_id(15)
print(preview.preview)  # HTML string
```

### Creating Campaigns

#### `create_campaign(name, subject, list_ids, from_email, campaign_type, content_type, body, alt_body, send_at, messenger, template_id, tags, headers, timeout_config) -> Optional[Campaign]`

All parameters except `name` and `subject` are optional.

```python
from datetime import datetime, timedelta

campaign = listmonk.create_campaign(
    name='Weekly Update',
    subject='This Week at Acme',
    body='<p>Hello {{ .Subscriber.FirstName }}!</p>',
    alt_body='Hello!',                              # Plain text fallback
    list_ids={1, 2},                                # Default: {1}
    template_id=5,                                  # Default: None
    content_type='html',                            # 'richtext', 'html', 'markdown', 'plain'
    send_at=datetime.now() + timedelta(hours=1),    # Schedule for later
    tags=['weekly', 'update'],
    from_email='newsletter@yourdomain.com',
    headers={'X-Custom-Header': 'value'},
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | required | Campaign name |
| `subject` | `str` | required | Email subject line |
| `list_ids` | `set[int]` | `{1}` | Target lists |
| `body` | `str` | `None` | Campaign body (HTML/markdown/plain) |
| `alt_body` | `str` | `None` | Plain text alternative |
| `template_id` | `int` | `None` | Template to wrap the body |
| `content_type` | `str` | `None` | `'richtext'`, `'html'`, `'markdown'`, `'plain'` |
| `campaign_type` | `str` | `None` | `'regular'` or `'optin'` |
| `send_at` | `datetime` | `None` | Scheduled send time |
| `from_email` | `str` | `None` | Sender address (uses server default if omitted) |
| `messenger` | `str` | `None` | Usually `'email'` |
| `tags` | `list[str]` | `[]` | Tags for organization |
| `headers` | `dict` | `{}` | Custom email headers |

### Updating Campaigns

#### `update_campaign(campaign: Campaign, timeout_config: Optional[httpx.Timeout] = None) -> Optional[Campaign]`

Update an existing campaign. Modify fields on the Campaign object, then pass it back.

```python
campaign = listmonk.campaign_by_id(15)
campaign.name = 'Better Name'
campaign.subject = 'Updated Subject'
campaign.body = '<p>New content</p>'
campaign.lists = [3, 4]  # Change target lists

updated = listmonk.update_campaign(campaign)
```

**Note:** If the campaign's `send_at` is in the past, it is automatically set to `None` (removing the schedule) to prevent API errors.

### Deleting Campaigns

#### `delete_campaign(campaign_id: Optional[int] = None, timeout_config: Optional[httpx.Timeout] = None) -> bool`

Delete a campaign by ID.

```python
deleted = listmonk.delete_campaign(15)
```

---

## Templates

### Retrieving Templates

#### `templates(timeout_config: Optional[httpx.Timeout] = None) -> list[Template]`

Get all templates.

```python
all_templates = listmonk.templates()
for t in all_templates:
    print(f'{t.name} (type: {t.type}, default: {t.is_default})')
```

#### `template_by_id(template_id: int, timeout_config: Optional[httpx.Timeout] = None) -> Optional[Template]`

Get a single template by ID.

```python
template = listmonk.template_by_id(2)
```

#### `template_preview_by_id(template_id: int, timeout_config: Optional[httpx.Timeout] = None) -> Optional[TemplatePreview]`

Get a rendered preview of a template (with lorem ipsum content).

```python
preview = listmonk.template_preview_by_id(3)
print(preview.preview)
```

### Creating Templates

#### `create_template(name: Optional[str], body: Optional[str], type: Optional[str], is_default: Optional[bool], subject: Optional[str], timeout_config: Optional[httpx.Timeout] = None) -> Optional[Template]`

Create a new template.

```python
# Campaign template — must include the content placeholder
campaign_tpl = listmonk.create_template(
    name='My Campaign Template',
    body='<html><body>{{ template "content" . }}</body></html>',
    type='campaign',
)

# Transactional template
tx_tpl = listmonk.create_template(
    name='Password Reset',
    subject='Reset Your Password',
    body='<p>Hi {{ .Subscriber.FirstName }}, your code: {{ template "content" . }}</p>',
    type='tx',
)
```

**Important:** The body **must** contain `{{ template "content" . }}` exactly once, or a `ValueError` is raised.

**Template types:** `'campaign'` or `'tx'` (transactional).

### Updating Templates

#### `update_template(template: Template, timeout_config: Optional[httpx.Timeout] = None) -> Optional[Template]`

Update an existing template.

```python
template = listmonk.template_by_id(2)
template.name = "Bob's Great Template"
template.body = '<html><body>{{ template "content" . }}</body></html>'

updated = listmonk.update_template(template)
```

### Deleting Templates

#### `delete_template(template_id: Optional[int] = None, timeout_config: Optional[httpx.Timeout] = None) -> bool`

Delete a template by ID.

```python
deleted = listmonk.delete_template(3)
```

### Setting Default Template

#### `set_default_template(template_id: Optional[int] = None, timeout_config: Optional[httpx.Timeout] = None) -> bool`

Set a template as the default for its type.

```python
listmonk.set_default_template(5)
```

---

## Transactional Email

### `send_transactional_email(subscriber_email, template_id, from_email, template_data, messenger_channel, content_type, attachments, email_headers, timeout_config) -> bool`

Send a one-off transactional email (e.g. password resets, order confirmations).

```python
# Basic transactional email
success = listmonk.send_transactional_email(
    subscriber_email='user@example.com',
    template_id=3,                          # Must be a *transactional* template
    from_email='app@yourdomain.com',        # Optional, uses server default
    template_data={                          # Available as {{ .Tx.Data.* }} in template
        'full_name': 'Jane Doe',
        'reset_code': 'abc123',
    },
    content_type='html',                    # 'html', 'markdown', or 'plain'
)
```

**With attachments:**

```python
from pathlib import Path

success = listmonk.send_transactional_email(
    subscriber_email='user@example.com',
    template_id=3,
    template_data={'order_id': 1772},
    attachments=[
        Path('/path/to/invoice.pdf'),
        Path('/path/to/receipt.png'),
    ],
    content_type='html',
)
```

**With custom headers:**

```python
success = listmonk.send_transactional_email(
    subscriber_email='user@example.com',
    template_id=3,
    email_headers=[
        {'X-Custom-Header': 'value'},
        {'X-Priority': '1'},
    ],
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `subscriber_email` | `str` | required | Recipient (must be an existing subscriber) |
| `template_id` | `int` | required | Transactional template ID |
| `from_email` | `str` | `None` | Sender address |
| `template_data` | `dict` | `None` | Merge data for template (`{{ .Tx.Data.key }}`) |
| `messenger_channel` | `str` | `'email'` | Delivery channel |
| `content_type` | `str` | `'markdown'` | `'html'`, `'markdown'`, `'plain'` |
| `attachments` | `list[Path]` | `None` | File attachments |
| `email_headers` | `list[dict]` | `None` | Custom email headers |

Raises `ListmonkFileNotFoundError` if any attachment path doesn't exist.

---

## Models Reference

All models are Pydantic `BaseModel` subclasses, importable from `listmonk.models`.

```python
from listmonk.models import (
    Subscriber, MailingList, Campaign, Template,
    CampaignPreview, TemplatePreview, SubscriberStatuses,
)
```

### `SubscriberStatuses` (Enum)

```python
class SubscriberStatuses(LowercaseStrEnum):
    enabled = 'enabled'
    disabled = 'disabled'
    blocklisted = 'blocklisted'
```

### `MailingList`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | List ID |
| `created_at` | `datetime` | Creation timestamp |
| `updated_at` | `Optional[datetime]` | Last update timestamp |
| `uuid` | `str` | List UUID |
| `name` | `Optional[str]` | List name |
| `type` | `Optional[str]` | `'public'` or `'private'` |
| `optin` | `Optional[str]` | `'single'` or `'double'` |
| `tags` | `list[str]` | Associated tags |
| `description` | `Optional[str]` | List description |
| `subscriber_count` | `Optional[int]` | Number of subscribers |

### `Subscriber`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Subscriber ID |
| `email` | `str` | Email address |
| `name` | `str` | Full name |
| `created_at` | `datetime` | Creation timestamp |
| `updated_at` | `Optional[datetime]` | Last update timestamp |
| `uuid` | `Optional[str]` | Subscriber UUID |
| `lists` | `list[dict]` | Lists the subscriber belongs to |
| `attribs` | `dict[str, Any]` | Custom attributes (queryable) |
| `status` | `Optional[str]` | `'enabled'`, `'disabled'`, or `'blocklisted'` |

### `Campaign`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Campaign ID |
| `created_at` | `datetime` | Creation timestamp |
| `updated_at` | `Optional[datetime]` | Last update timestamp |
| `uuid` | `str` | Campaign UUID |
| `name` | `Optional[str]` | Campaign name |
| `type` | `Optional[str]` | `'regular'` or `'optin'` |
| `subject` | `Optional[str]` | Email subject |
| `from_email` | `Optional[str]` | Sender email |
| `body` | `Optional[str]` | Campaign body content |
| `altbody` | `Optional[str]` | Plain text alternative |
| `status` | `Optional[str]` | Campaign status |
| `content_type` | `Optional[str]` | Content format |
| `template_id` | `int` | Template ID used |
| `send_at` | `Optional[datetime]` | Scheduled send time |
| `started_at` | `Optional[datetime]` | When sending began |
| `lists` | `list[dict]` | Target lists |
| `tags` | `list[str]` | Campaign tags |
| `views` | `int` | View count |
| `clicks` | `int` | Click count |
| `to_send` | `int` | Total recipients |
| `sent` | `int` | Emails sent so far |
| `messenger` | `Optional[str]` | Delivery channel |
| `headers` | `dict[str, Optional[str]]` | Custom headers |

### `Template`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Template ID |
| `created_at` | `datetime` | Creation timestamp |
| `updated_at` | `Optional[datetime]` | Last update timestamp |
| `name` | `Optional[str]` | Template name |
| `subject` | `Optional[str]` | Subject (for transactional templates) |
| `body` | `Optional[str]` | Template HTML body |
| `type` | `Optional[str]` | `'campaign'` or `'tx'` |
| `is_default` | `Optional[bool]` | Whether this is the default template |

### `CampaignPreview` / `TemplatePreview`

| Field | Type | Description |
|-------|------|-------------|
| `preview` | `Optional[str]` | Rendered HTML preview string |

---

## Errors

Custom exceptions are in `listmonk.errors`.

```python
from listmonk.errors import ValidationError, OperationNotAllowedError, ListmonkFileNotFoundError
```

| Exception | Parent | When Raised |
|-----------|--------|-------------|
| `ValidationError` | `Exception` | Invalid input, empty responses, malformed JSON |
| `OperationNotAllowedError` | `ValidationError` | Calling API before `set_url_base()` or `login()` |
| `ListmonkFileNotFoundError` | `FileNotFoundError` | Attachment file doesn't exist |

Additionally, `httpx.HTTPStatusError` may be raised on HTTP 4xx/5xx responses.

---

## API Endpoints

The library targets these Listmonk API endpoints (defined in `listmonk.urls`):

| Constant | Path | Used By |
|----------|------|---------|
| `health` | `/api/health` | `is_healthy()`, `verify_login()` |
| `lists` | `/api/lists` | `lists()`, `create_list()` |
| `lst` | `/api/lists/{list_id}` | `list_by_id()`, `delete_list()`, `update_list()` |
| `subscribers` | `/api/subscribers` | `subscribers()`, `subscriber_by_*()`, `create_subscriber()` |
| `subscriber` | `/api/subscribers/{subscriber_id}` | `update_subscriber()`, `delete_subscriber()` |
| `subscriber_lists` | `/api/subscribers/lists` | `add_subscribers_to_lists()` |
| `opt_in` | `/subscription/optin/{subscriber_uuid}` | `confirm_optin()` |
| `send_tx` | `/api/tx` | `send_transactional_email()` |
| `campaigns` | `/api/campaigns` | `campaigns()`, `create_campaign()` |
| `campaign_id` | `/api/campaigns/{campaign_id}` | `campaign_by_id()`, `update_campaign()`, `delete_campaign()` |
| `campaign_id_preview` | `/api/campaigns/{campaign_id}/preview` | `campaign_preview_by_id()` |
| `templates` | `/api/templates` | `templates()`, `create_template()` |
| `template_id` | `/api/templates/{template_id}` | `template_by_id()`, `update_template()`, `delete_template()` |
| `template_id_preview` | `/api/templates/{template_id}/preview` | `template_preview_by_id()` |
| `template_id_default` | `/api/templates/{template_id}/default` | `set_default_template()` |

---

## FAQ / Troubleshooting

### `httpx.HTTPStatusError: Client error '403 Forbidden'`

```text
httpx.HTTPStatusError: Client error '403 Forbidden' for url '...?query=subscribers.email=...'
```

The authenticated user lacks the `subscribers:sql_query` permission. Update the user's role in the Listmonk admin panel to include this permission. See [Listmonk roles docs](https://listmonk.app/docs/roles-and-permissions/#user-roles).

### Required Call Order

You **must** call functions in this order:

1. `listmonk.set_url_base('...')`
2. `listmonk.login('user', 'pass')`
3. Any other API call

Calling API functions before setup raises `OperationNotAllowedError`.

### Timeouts

All functions accept an optional `timeout_config` parameter (default: 10 seconds):

```python
import httpx

# Custom timeout for slow connections
timeout = httpx.Timeout(timeout=30.0)
subs = listmonk.subscribers(timeout_config=timeout)
```

### Global State

The library uses module-level global variables for authentication. This means:
- Credentials persist for the application lifetime
- Only one Listmonk instance can be configured at a time
- Thread safety is not guaranteed for credential changes

---

## Complete Public API

All public functions exported by `listmonk`:

| Function | Category | Returns |
|----------|----------|---------|
| `set_url_base(url)` | Config | `None` |
| `get_base_url()` | Config | `Optional[str]` |
| `login(user, pw)` | Auth | `bool` |
| `verify_login()` | Auth | `bool` |
| `is_healthy()` | Health | `bool` |
| `lists()` | Lists | `list[MailingList]` |
| `list_by_id(id)` | Lists | `Optional[MailingList]` |
| `create_list(name, ...)` | Lists | `Optional[MailingList]` |
| `update_list(id, ...)` | Lists | `Optional[MailingList]` |
| `delete_list(id)` | Lists | `bool` |
| `subscribers(query, list_id)` | Subscribers | `list[Subscriber]` |
| `subscriber_by_email(email)` | Subscribers | `Optional[Subscriber]` |
| `subscriber_by_id(id)` | Subscribers | `Optional[Subscriber]` |
| `subscriber_by_uuid(uuid)` | Subscribers | `Optional[Subscriber]` |
| `create_subscriber(email, name, ...)` | Subscribers | `Subscriber` |
| `update_subscriber(sub, add, remove)` | Subscribers | `Optional[Subscriber]` |
| `disable_subscriber(sub)` | Subscribers | `Optional[Subscriber]` |
| `enable_subscriber(sub)` | Subscribers | `Optional[Subscriber]` |
| `block_subscriber(sub)` | Subscribers | `Optional[Subscriber]` |
| `delete_subscriber(email)` | Subscribers | `bool` |
| `add_subscribers_to_lists(ids, lists)` | Subscribers | `bool` |
| `confirm_optin(sub_uuid, list_uuid)` | Subscribers | `bool` |
| `campaigns()` | Campaigns | `list[Campaign]` |
| `campaign_by_id(id)` | Campaigns | `Optional[Campaign]` |
| `campaign_preview_by_id(id)` | Campaigns | `Optional[CampaignPreview]` |
| `create_campaign(name, subject, ...)` | Campaigns | `Optional[Campaign]` |
| `update_campaign(campaign)` | Campaigns | `Optional[Campaign]` |
| `delete_campaign(id)` | Campaigns | `bool` |
| `templates()` | Templates | `list[Template]` |
| `template_by_id(id)` | Templates | `Optional[Template]` |
| `template_preview_by_id(id)` | Templates | `Optional[TemplatePreview]` |
| `create_template(name, body, ...)` | Templates | `Optional[Template]` |
| `update_template(template)` | Templates | `Optional[Template]` |
| `delete_template(id)` | Templates | `bool` |
| `set_default_template(id)` | Templates | `bool` |
| `send_transactional_email(email, ...)` | Transactional | `bool` |
