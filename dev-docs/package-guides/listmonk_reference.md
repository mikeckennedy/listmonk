# listmonk — Comprehensive API Reference

> Python client library for the open-source, self-hosted [Listmonk](https://listmonk.app) email platform.
> Built on [httpx2](https://github.com/pydantic/httpx2) and [Pydantic](https://pydantic.dev). Supports Python 3.10+.

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

Dependencies: `httpx2`, `pydantic`, `strenum`

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

### `login(user_name: str, pw: str, timeout_config: Optional[httpx2.Timeout] = None) -> bool`

Authenticate with your Listmonk instance. Must call `set_url_base()` first.

```python
success = listmonk.login('admin', 'secretpassword')
```

- Validates credentials against the server immediately
- Returns `True` if authentication succeeded, `False` otherwise
- Raises `OperationNotAllowedError` if `set_url_base()` has not been called
- Raises `ValidationError` if username or password is empty

### `verify_login(timeout_config: Optional[httpx2.Timeout] = None) -> bool`

Verify that stored credentials are still valid.

```python
still_valid = listmonk.verify_login()
```

---

## Health Check

### `is_healthy(timeout_config: Optional[httpx2.Timeout] = None) -> bool`

Check if the Listmonk instance is alive and accessible with current credentials.

```python
if listmonk.is_healthy():
    print('Listmonk is up!')
```

Returns `False` on any error (network, auth, etc.) rather than raising.

---

## Subscribers

### Retrieving Subscribers

#### `subscribers(query_text: Optional[str] = None, list_id: Optional[int] = None, timeout_config: Optional[httpx2.Timeout] = None) -> list[Subscriber]`

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

#### `subscriber_by_email(email: str, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[Subscriber]`

Look up a single subscriber by email address.

```python
sub = listmonk.subscriber_by_email('user@example.com')
if sub:
    print(f'{sub.name} (ID: {sub.id})')
```

Returns `None` if not found.

#### `subscriber_by_id(subscriber_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[Subscriber]`

Look up a single subscriber by their numeric ID.

```python
sub = listmonk.subscriber_by_id(2001)
```

Returns `None` if not found.

#### `subscriber_by_uuid(subscriber_uuid: str, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[Subscriber]`

Look up a single subscriber by their UUID.

```python
sub = listmonk.subscriber_by_uuid('f6668cf0-1c2e-...')
```

Returns `None` if not found.

### Creating Subscribers

#### `create_subscriber(email: str, name: str, list_ids: set[int], pre_confirm: bool, attribs: dict[str, Any], timeout_config: Optional[httpx2.Timeout] = None) -> Subscriber`

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

#### `update_subscriber(subscriber: Optional[Subscriber], add_to_lists: Optional[set[int]] = None, remove_from_lists: Optional[set[int]] = None, status: SubscriberStatuses = SubscriberStatuses.enabled, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[Subscriber]`

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

#### `disable_subscriber(subscriber: Optional[Subscriber], timeout_config: Optional[httpx2.Timeout] = None) -> Optional[Subscriber]`

Set a subscriber's status to "disabled".

```python
disabled = listmonk.disable_subscriber(subscriber)
```

#### `enable_subscriber(subscriber: Subscriber, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[Subscriber]`

Re-enable a disabled subscriber.

```python
enabled = listmonk.enable_subscriber(subscriber)
```

#### `block_subscriber(subscriber: Subscriber, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[Subscriber]`

Blocklist (unsubscribe) a subscriber. This is the equivalent of "unsubscribe" — they remain in the system but won't receive emails.

```python
listmonk.block_subscriber(subscriber)
```

### Deleting Subscribers

#### `delete_subscriber(email: Optional[str] = None, overriding_subscriber_id: Optional[int] = None, timeout_config: Optional[httpx2.Timeout] = None) -> bool`

Permanently delete a subscriber. If you want to unsubscribe instead, use `block_subscriber`.

```python
# Delete by email
deleted = listmonk.delete_subscriber('user@example.com')

# Delete by ID (takes precedence over email)
deleted = listmonk.delete_subscriber(overriding_subscriber_id=2001)
```

Returns `True` on success, `False` if subscriber not found.

### Opt-in Confirmation

#### `confirm_optin(subscriber_uuid: Optional[str], list_uuid: Optional[str], timeout_config: Optional[httpx2.Timeout] = None) -> bool`

Confirm a subscriber's opt-in for a specific list via the API (for double opt-in lists).

```python
confirmed = listmonk.confirm_optin(subscriber.uuid, mailing_list.uuid)
```

Use this when you manage opt-in confirmation on your own platform rather than through Listmonk's built-in email flow.

### Bulk List Management

#### `add_subscribers_to_lists(subscriber_ids: Iterable[int], list_ids: Iterable[int], timeout_config: Optional[httpx2.Timeout] = None, status: str = 'confirmed') -> bool`

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

### `lists(timeout_config: Optional[httpx2.Timeout] = None) -> list[MailingList]`

Get all mailing lists.

```python
all_lists = listmonk.lists()
for lst in all_lists:
    print(f'{lst.name}: {lst.subscriber_count} subscribers')
```

### `list_by_id(list_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[MailingList]`

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

#### `campaigns(timeout_config: Optional[httpx2.Timeout] = None) -> list[Campaign]`

Get all campaigns.

```python
all_campaigns = listmonk.campaigns()
for c in all_campaigns:
    print(f'{c.name}: {c.status} ({c.sent}/{c.to_send} sent)')
```

#### `campaign_by_id(campaign_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[Campaign]`

Get a single campaign by ID.

```python
campaign = listmonk.campaign_by_id(15)
```

#### `campaign_preview_by_id(campaign_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[CampaignPreview]`

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

#### `update_campaign(campaign: Campaign, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[Campaign]`

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

#### `delete_campaign(campaign_id: Optional[int] = None, timeout_config: Optional[httpx2.Timeout] = None) -> bool`

Delete a campaign by ID.

```python
deleted = listmonk.delete_campaign(15)
```

---

## Templates

### Retrieving Templates

#### `templates(timeout_config: Optional[httpx2.Timeout] = None) -> list[Template]`

Get all templates.

```python
all_templates = listmonk.templates()
for t in all_templates:
    print(f'{t.name} (type: {t.type}, default: {t.is_default})')
```

#### `template_by_id(template_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[Template]`

Get a single template by ID.

```python
template = listmonk.template_by_id(2)
```

#### `template_preview_by_id(template_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[TemplatePreview]`

Get a rendered preview of a template (with lorem ipsum content).

```python
preview = listmonk.template_preview_by_id(3)
print(preview.preview)
```

### Creating Templates

#### `create_template(name: Optional[str], body: Optional[str], type: Optional[str], is_default: Optional[bool], subject: Optional[str], timeout_config: Optional[httpx2.Timeout] = None) -> Optional[Template]`

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

#### `update_template(template: Template, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[Template]`

Update an existing template.

```python
template = listmonk.template_by_id(2)
template.name = "Bob's Great Template"
template.body = '<html><body>{{ template "content" . }}</body></html>'

updated = listmonk.update_template(template)
```

### Deleting Templates

#### `delete_template(template_id: Optional[int] = None, timeout_config: Optional[httpx2.Timeout] = None) -> bool`

Delete a template by ID.

```python
deleted = listmonk.delete_template(3)
```

### Setting Default Template

#### `set_default_template(template_id: Optional[int] = None, timeout_config: Optional[httpx2.Timeout] = None) -> bool`

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

Additionally, `httpx2.HTTPStatusError` may be raised on HTTP 4xx/5xx responses.

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

### `httpx2.HTTPStatusError: Client error '403 Forbidden'`

```text
httpx2.HTTPStatusError: Client error '403 Forbidden' for url '...?query=subscribers.email=...'
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
import httpx2

# Custom timeout for slow connections
timeout = httpx2.Timeout(timeout=30.0)
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

---

## Listmonk Server REST API Reference

> Complete reference for the Listmonk server's HTTP REST API. All endpoints return JSON with `Content-Type: application/json` unless otherwise noted. This section documents what the server expects — useful for understanding what our Python client is doing under the hood, and for operations not yet wrapped by the client.

### Authentication

API requests support two auth methods. Users and tokens are managed in the Listmonk admin UI (Admin -> Users).

**BasicAuth:**
```shell
curl -u "api_user:token" http://localhost:9000/api/lists
```

**Authorization token header:**
```shell
curl -H "Authorization: token api_user:token" http://localhost:9000/api/lists
```

### Permissions

- **User role**: Permissions (e.g. `subscribers:sql_query`) are defined as a *User role* (Admin -> User roles) and attached to a user.
- **List role**: Per-list read/write permissions are defined as a *List role* and attached to a user.
- `lists:get_all` or `lists:manage_all` in a User role overrides any List role restrictions.

### Response Structure

**Success (200):**
```json
{
    "data": { ... }
}
```

**Error (4xx/5xx):**
```json
{
    "message": "Error message"
}
```

### Timestamps

Format: `2019-01-01T09:00:00.000000+05:30` (milliseconds + timezone offset).

### Common HTTP Error Codes

| Code | Description |
|------|-------------|
| 400 | Missing or bad request parameters or values |
| 403 | Session expired or invalidated |
| 404 | Resource not found |
| 405 | Method not allowed on endpoint |
| 410 | Resource permanently gone |
| 422 | Unprocessable entity (invalid data) |
| 429 | Rate limited |
| 500 | Internal server error |

### OpenAPI Spec

Available at [listmonk.app/docs/swagger](https://listmonk.app/docs/swagger/)

---

### Subscribers API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/subscribers` | Query and retrieve subscribers |
| GET | `/api/subscribers/{id}` | Retrieve a specific subscriber |
| GET | `/api/subscribers/{id}/export` | Export subscriber data (profile, lists, views, clicks) |
| GET | `/api/subscribers/{id}/bounces` | Get subscriber's bounce records |
| POST | `/api/subscribers` | Create a new subscriber |
| POST | `/api/subscribers/{id}/optin` | Send opt-in confirmation email |
| POST | `/api/public/subscription` | Create a public subscription (unauthenticated) |
| PUT | `/api/subscribers/lists` | Modify subscriber list memberships in bulk |
| PUT | `/api/subscribers/{id}` | Full update of a subscriber (replaces all fields) |
| PATCH | `/api/subscribers/{id}` | Partial update (only provided fields change) |
| PUT | `/api/subscribers/{id}/blocklist` | Blocklist a specific subscriber |
| PUT | `/api/subscribers/blocklist` | Blocklist multiple subscribers by IDs |
| PUT | `/api/subscribers/query/blocklist` | Blocklist subscribers matching SQL expression |
| DELETE | `/api/subscribers/{id}` | Delete a specific subscriber |
| DELETE | `/api/subscribers/{id}/bounces` | Delete a subscriber's bounce records |
| DELETE | `/api/subscribers` | Delete multiple subscribers by IDs |
| POST | `/api/subscribers/query/delete` | Delete subscribers matching SQL expression |

#### GET /api/subscribers

Query parameters:

| Name | Type | Description |
|------|------|-------------|
| `query` | string | SQL expression for subscriber search |
| `list_id` | int[] | List IDs to filter by (repeat for multiple) |
| `subscription_status` | string | Filter by subscription status when `list_id` is set |
| `order_by` | string | Sort field: `name`, `status`, `created_at`, `updated_at` |
| `order` | string | `ASC` or `DESC` |
| `page` | number | Page number |
| `per_page` | number | Results per page (use `'all'` for everything) |

```shell
# All subscribers, paginated
curl -u 'user:token' 'http://localhost:9000/api/subscribers?page=1&per_page=100'

# Filter by list
curl -u 'user:token' 'http://localhost:9000/api/subscribers?list_id=1&list_id=2&page=1&per_page=100'

# SQL query filtering
curl -u 'user:token' -X GET 'http://localhost:9000/api/subscribers' \
    --url-query "query=subscribers.name LIKE 'Test%' AND subscribers.attribs->>'city' = 'Bengaluru'"
```

Example response:
```json
{
    "data": {
        "results": [
            {
                "id": 1,
                "created_at": "2020-02-10T23:07:16.199433+01:00",
                "updated_at": "2020-02-10T23:07:16.199433+01:00",
                "uuid": "ea06b2e7-4b08-4697-bcfc-2a5c6dde8f1c",
                "email": "john@example.com",
                "name": "John Doe",
                "attribs": { "city": "Bengaluru", "good": true, "type": "known" },
                "status": "enabled",
                "lists": [
                    {
                        "subscription_status": "unconfirmed",
                        "id": 1, "uuid": "ce13e971-...", "name": "Default list",
                        "type": "public", "tags": ["test"],
                        "created_at": "2020-02-10T23:07:16.194843+01:00",
                        "updated_at": "2020-02-10T23:07:16.194843+01:00"
                    }
                ]
            }
        ],
        "query": "",
        "total": 3,
        "per_page": 20,
        "page": 1
    }
}
```

#### POST /api/subscribers

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `email` | string | Yes | Email address |
| `name` | string | Yes | Subscriber name |
| `status` | string | Yes | `enabled` or `blocklisted` |
| `lists` | number[] | | List IDs to subscribe to |
| `attribs` | JSON | | Custom attributes (e.g. `{"city": "Portland"}`) |
| `preconfirm_subscriptions` | bool | | Skip double opt-in confirmation |

```shell
curl -u 'user:token' 'http://localhost:9000/api/subscribers' \
    -H 'Content-Type: application/json' \
    --data '{"email":"sub@domain.com","name":"The Sub","status":"enabled","lists":[1],"attribs":{"city":"Bengaluru"}}'
```

#### PUT vs PATCH /api/subscribers/{id}

**PUT** (full update): All parameters must be set. Omitting `lists` clears all list subscriptions.

**PATCH** (partial update): Only fields present in the request body are updated. Omitting `lists` preserves existing subscriptions. Attributes are merged, not replaced.

```shell
# Partial update — only changes the name, keeps everything else
curl -u 'user:token' -X PATCH 'http://localhost:9000/api/subscribers/1' \
    -H 'Content-Type: application/json' \
    --data '{"name":"Updated Name"}'
```

#### PUT /api/subscribers/lists (Bulk List Management)

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ids` | number[] | Yes | Subscriber IDs |
| `action` | string | Yes | `add`, `remove`, or `unsubscribe` |
| `target_list_ids` | number[] | Yes | List IDs to modify |
| `status` | string | For `add` | `confirmed`, `unconfirmed`, or `unsubscribed` |

```shell
curl -u 'user:token' -X PUT 'http://localhost:9000/api/subscribers/lists' \
    -H 'Content-Type: application/json' \
    --data '{"ids": [1, 2, 3], "action": "add", "target_list_ids": [4, 5], "status": "confirmed"}'
```

#### POST /api/public/subscription (Unauthenticated)

For public-facing subscription forms. Accepts form-encoded or JSON.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `email` | string | Yes | Email address |
| `name` | string | | Subscriber name |
| `list_uuids` | string[] | Yes | List UUIDs (not IDs) |

#### Blocklist Operations

```shell
# Single subscriber
curl -u 'user:token' -X PUT 'http://localhost:9000/api/subscribers/9/blocklist'

# Multiple by IDs
curl -u 'user:token' -X PUT 'http://localhost:9000/api/subscribers/blocklist' \
    -H 'Content-Type: application/json' --data '{"ids":[2,1]}'

# By SQL query
curl -u 'user:token' -X POST 'http://localhost:9000/api/subscribers/query/blocklist' \
    -H 'Content-Type: application/json' \
    --data '{"query":"subscribers.name LIKE '\''John%'\''"}'
```

#### Delete Operations

```shell
# Single subscriber
curl -u 'user:token' -X DELETE 'http://localhost:9000/api/subscribers/9'

# Multiple by IDs
curl -u 'user:token' -X DELETE 'http://localhost:9000/api/subscribers?id=10&id=11'

# By SQL query
curl -u 'user:token' -X POST 'http://localhost:9000/api/subscribers/query/delete' \
    -H 'Content-Type: application/json' \
    --data '{"query":"subscribers.attribs->>'\''city'\'' = '\''Bengaluru'\''"}'
```

---

### Lists API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lists` | Retrieve lists (with filtering) |
| GET | `/api/public/lists` | Public lists (unauthenticated, active + public only) |
| GET | `/api/lists/{id}` | Retrieve a specific list |
| POST | `/api/lists` | Create a new list |
| PUT | `/api/lists/{id}` | Update a list |
| DELETE | `/api/lists/{id}` | Delete a list |
| DELETE | `/api/lists` | Delete multiple lists (by IDs or search query) |

#### GET /api/lists

| Name | Type | Description |
|------|------|-------------|
| `query` | string | Search by list name |
| `status` | string | `active` or `archived` (default: all) |
| `minimal` | boolean | If `true`, omits subscriber counts (faster) |
| `tag` | string[] | Filter by tags (repeat for multiple) |
| `order_by` | string | `name`, `status`, `created_at`, `updated_at` |
| `order` | string | `ASC` or `DESC` |
| `page` | number | Page number |
| `per_page` | number | Results per page (`'all'` for everything) |

> **Note:** Archived lists (`status: archived`) are hidden from campaign selectors, public subscription forms, and roles by default.

```shell
# Active lists only
curl -u "user:token" 'http://localhost:9000/api/lists?status=active&per_page=100'

# Archived, minimal (no subscriber counts)
curl -u "user:token" 'http://localhost:9000/api/lists?status=archived&minimal=true&per_page=all'
```

#### POST /api/lists

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `name` | string | Yes | List name |
| `type` | string | Yes | `private` or `public` |
| `optin` | string | Yes | `single` or `double` |
| `status` | string | | `active` (default) or `archived` |
| `tags` | string[] | | Associated tags |
| `description` | string | | List description |

#### DELETE /api/lists (Bulk)

Delete by IDs or search query:
```shell
# By IDs
curl -u "user:token" -X DELETE 'http://localhost:9000/api/lists?id=10&id=11'

# By search query
curl -u "user:token" -X DELETE 'http://localhost:9000/api/lists?query=test%20list'
```

---

### Campaigns API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/campaigns` | Retrieve all campaigns |
| GET | `/api/campaigns/{id}` | Retrieve a specific campaign |
| GET | `/api/campaigns/{id}/preview` | Preview rendered campaign HTML |
| GET | `/api/campaigns/running/stats` | Stats for running campaigns |
| GET | `/api/campaigns/analytics/{type}` | Analytics: `views`, `links`, `clicks`, `bounces` |
| POST | `/api/campaigns` | Create a new campaign |
| POST | `/api/campaigns/{id}/test` | Send test to arbitrary subscribers |
| PUT | `/api/campaigns/{id}` | Update a campaign |
| PUT | `/api/campaigns/{id}/status` | Change campaign status |
| PUT | `/api/campaigns/{id}/archive` | Publish to public archive |
| DELETE | `/api/campaigns/{id}` | Delete a campaign |
| DELETE | `/api/campaigns` | Delete multiple campaigns |

#### GET /api/campaigns

| Name | Type | Description |
|------|------|-------------|
| `query` | string | Search by name and subject (fulltext + substring) |
| `status` | string[] | Filter by status (repeat for multiple) |
| `tags` | string[] | Filter by tags (repeat for multiple) |
| `order_by` | string | `name`, `status`, `created_at`, `updated_at` |
| `order` | string | `ASC` or `DESC` |
| `page` | number | Page number |
| `per_page` | number | Results per page |
| `no_body` | boolean | Omit body content from response |

#### POST /api/campaigns

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `name` | string | Yes | Campaign name |
| `subject` | string | Yes | Email subject |
| `lists` | number[] | Yes | Target list IDs |
| `type` | string | Yes | `regular` or `optin` |
| `content_type` | string | Yes | `richtext`, `html`, `markdown`, `plain`, `visual` |
| `body` | string | Yes | Campaign body content |
| `body_source` | string | | JSON block source (for `visual` content type) |
| `from_email` | string | | Sender address (defaults to server setting) |
| `altbody` | string | | Plain text alternative |
| `send_at` | string | | Schedule: `YYYY-MM-DDTHH:MM:SSZ` |
| `messenger` | string | | `email` or custom messenger |
| `template_id` | number | | Template ID (defaults to default template) |
| `tags` | string[] | | Campaign tags |
| `headers` | JSON | | Custom SMTP headers: `[{"x-custom": "value"}]` |
| `attribs` | JSON | | Template attributes: `{"key": "value"}` |

#### PUT /api/campaigns/{id}/status

Change campaign lifecycle status:

| Status | Allowed Transitions |
|--------|-------------------|
| `draft` | -> `scheduled`, -> `running` |
| `scheduled` | -> `draft` |
| `running` | -> `paused`, -> `cancelled` |
| `paused` | -> `running` |

```shell
curl -u "user:token" -X PUT 'http://localhost:9000/api/campaigns/1/status' \
    -H 'Content-Type: application/json' \
    --data '{"status":"scheduled"}'
```

#### PUT /api/campaigns/{id}/archive

Publish a campaign to the public archive:

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `archive` | bool | Yes | Enable/disable public archive |
| `archive_template_id` | number | | Archive template ID |
| `archive_meta` | JSON | | Metadata for template (e.g. name, email) |
| `archive_slug` | string | | URL slug for the archive page |

```shell
curl -u "user:token" -X PUT 'http://localhost:9000/api/campaigns/33/archive' \
    -H 'Content-Type: application/json' \
    --data '{"archive":true,"archive_template_id":1,"archive_slug":"my-newsletter"}'
```

#### GET /api/campaigns/analytics/{type}

Retrieve campaign analytics over a date range.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | number[] | Yes | Campaign IDs |
| `type` | string | Yes | `views`, `links`, `clicks`, or `bounces` |
| `from` | string | Yes | Start date |
| `to` | string | Yes | End date |

```shell
# View counts over time
curl -u "user:token" 'http://localhost:9000/api/campaigns/analytics/views?id=1&from=2024-08-04&to=2024-08-12'

# Link click breakdown
curl -u "user:token" 'http://localhost:9000/api/campaigns/analytics/links?id=1&from=2024-08-04&to=2024-08-12'
```

#### POST /api/campaigns/{id}/test

Send a test email to arbitrary subscribers. Uses the same parameters as POST `/api/campaigns` plus:

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `subscribers` | string[] | Yes | Email addresses to send test to |

---

### Templates API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/templates` | Retrieve all templates |
| GET | `/api/templates/{id}` | Retrieve a specific template |
| GET | `/api/templates/{id}/preview` | Get rendered HTML preview |
| POST | `/api/templates` | Create a template |
| POST | `/api/templates/preview` | Render and preview a template |
| PUT | `/api/templates/{id}` | Update a template |
| PUT | `/api/templates/{id}/default` | Set as default template |
| DELETE | `/api/templates/{id}` | Delete a template |

#### POST /api/templates

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `name` | string | Yes | Template name |
| `type` | string | Yes | `campaign`, `campaign_visual`, or `tx` |
| `body` | string | Yes | HTML body |
| `subject` | string | | Subject line (for `tx` templates) |
| `body_source` | string | | JSON source (for `campaign_visual`) |

Template types:
- **`campaign`**: Standard campaign template. Body must contain `{{ template "content" . }}`.
- **`campaign_visual`**: Visual/drag-and-drop builder template. Includes `body_source` JSON.
- **`tx`**: Transactional email template with optional subject line.

---

### Transactional API

#### POST /api/tx

Send transactional messages via a preconfigured transactional template.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `subscriber_email` | string | | Recipient email (or use `subscriber_id`) |
| `subscriber_id` | number | | Recipient ID (or use `subscriber_email`) |
| `subscriber_emails` | string[] | | Multiple recipients |
| `subscriber_ids` | number[] | | Multiple recipient IDs |
| `subscriber_mode` | string | | `default`, `fallback`, or `external` |
| `template_id` | number | Yes | Transactional template ID |
| `from_email` | string | | Sender address |
| `subject` | string | | Overrides template subject |
| `data` | JSON | | Merge data: `{{ .Tx.Data.key }}` in templates |
| `headers` | JSON[] | | Custom email headers |
| `messenger` | string | | Delivery channel (default: `email`) |
| `content_type` | string | | `html`, `markdown`, or `plain` |
| `altbody` | string | | Plain text alternative for HTML emails |

#### Subscriber Modes

| Mode | Behavior |
|------|----------|
| `default` | Recipients must exist as subscribers. Use `subscriber_emails` or `subscriber_ids`. |
| `fallback` | Looks up subscriber by email; if not found, sends anyway. Only `{{ .Subscriber.Email }}` is available; use `{{ .Tx.Data.* }}` for other fields. |
| `external` | Sends to arbitrary emails without database lookup. Only `{{ .Subscriber.Email }}` is available. |

```shell
# Standard transactional email
curl -u "user:token" "http://localhost:9000/api/tx" -X POST \
    -H 'Content-Type: application/json' \
    --data '{"subscriber_email":"user@test.com","template_id":2,"data":{"order_id":"1234"},"content_type":"html"}'

# External mode — no subscriber required
curl -u "user:token" "http://localhost:9000/api/tx" -X POST \
    -H 'Content-Type: application/json' \
    --data '{"subscriber_mode":"external","subscriber_emails":["anyone@example.com"],"template_id":2,"data":{"name":"John"},"content_type":"html"}'
```

#### File Attachments

Use `multipart/form-data` with `data` as a JSON string and `file` params for attachments:

```shell
curl -u "user:token" "http://localhost:9000/api/tx" -X POST \
    -F 'data="{\"subscriber_email\":\"user@test.com\",\"template_id\":4}"' \
    -F 'file=@"/path/to/attachment.pdf"' \
    -F 'file=@"/path/to/attachment2.pdf"'
```

---

### Bounces API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/bounces` | Retrieve bounce records |
| DELETE | `/api/bounces` | Delete all or multiple bounce records |
| DELETE | `/api/bounces/{id}` | Delete a specific bounce record |

#### GET /api/bounces

| Name | Type | Description |
|------|------|-------------|
| `campaign_id` | number | Filter by campaign |
| `page` | number | Page number |
| `per_page` | number | Results per page (`'all'` for everything) |
| `source` | string | Filter by bounce source |
| `order_by` | string | `email`, `campaign_name`, `source`, `created_at` |
| `order` | string | `asc` or `desc` |

Example bounce record:
```json
{
    "id": 839971,
    "type": "hard",
    "source": "demo",
    "meta": { "some": "parameter" },
    "created_at": "2024-08-20T23:54:22.851858Z",
    "email": "user@example.com",
    "subscriber_uuid": "32ca1f3e-...",
    "subscriber_id": 60,
    "campaign": { "id": 1, "name": "Test campaign" }
}
```

#### DELETE /api/bounces

```shell
# Delete all bounces
curl -u 'user:token' -X DELETE 'http://localhost:9000/api/bounces?all=true'

# Delete specific bounces by ID
curl -u 'user:token' -X DELETE 'http://localhost:9000/api/bounces?id=123&id=456'

# Delete single bounce
curl -u 'user:token' -X DELETE 'http://localhost:9000/api/bounces/123'
```

---

### Import API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/import/subscribers` | Check import status |
| GET | `/api/import/subscribers/logs` | Retrieve import logs |
| POST | `/api/import/subscribers` | Upload CSV/ZIP for bulk import |
| DELETE | `/api/import/subscribers` | Stop and remove an import |

#### POST /api/import/subscribers

Upload a CSV (optionally ZIP compressed) file via `multipart/form-data`.

**`params` JSON string:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `mode` | string | Yes | `subscribe` or `blocklist` |
| `delim` | string | Yes | CSV delimiter (e.g. `,`) |
| `lists` | number[] | | List IDs to subscribe to |
| `overwrite` | bool | | Overwrite existing subscribers or skip |

```shell
curl -u "user:token" -X POST 'http://localhost:9000/api/import/subscribers' \
    -F 'params={"mode":"subscribe","subscription_status":"confirmed","delim":",","lists":[1,2],"overwrite":true}' \
    -F "file=@/path/to/subs.csv"
```

---

### Media API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/media` | List uploaded media files |
| GET | `/api/media/{id}` | Get a specific media file |
| POST | `/api/media` | Upload a media file |
| DELETE | `/api/media/{id}` | Delete a media file |

#### POST /api/media

Upload via `multipart/form-data`:

```shell
curl -u "user:token" -X POST 'http://localhost:9000/api/media' \
    -H 'Content-Type: multipart/form-data' \
    --form 'file=@/path/to/image.jpg'
```

Example response:
```json
{
    "data": {
        "id": 1,
        "uuid": "ec7b45ce-...",
        "filename": "image.jpg",
        "created_at": "2020-04-08T22:43:45.080058+01:00",
        "thumb_uri": "/uploads/image_thumb.jpg",
        "uri": "/uploads/image.jpg"
    }
}
```

---

### Python Client Coverage vs Server API

The following server endpoints are **not yet wrapped** by this Python client library:

| Endpoint | Description |
|----------|-------------|
| `PATCH /api/subscribers/{id}` | Partial subscriber update (preserves lists) |
| `GET /api/subscribers/{id}/export` | Export subscriber data |
| `GET /api/subscribers/{id}/bounces` | Subscriber bounce records |
| `DELETE /api/subscribers/{id}/bounces` | Delete subscriber bounces |
| `POST /api/subscribers/{id}/optin` | Send opt-in email |
| `POST /api/public/subscription` | Public subscription form |
| `PUT /api/subscribers/query/blocklist` | Blocklist by SQL query |
| `POST /api/subscribers/query/delete` | Delete by SQL query |
| `GET /api/campaigns/running/stats` | Running campaign stats |
| `GET /api/campaigns/analytics/{type}` | Campaign analytics (views/clicks/links/bounces) |
| `POST /api/campaigns/{id}/test` | Send test email |
| `PUT /api/campaigns/{id}/status` | Change campaign status |
| `PUT /api/campaigns/{id}/archive` | Publish to public archive |
| `POST /api/templates/preview` | Render and preview a template |
| Transactional `subscriber_mode` | `fallback` and `external` modes |
| Transactional `subscriber_ids`/`subscriber_emails` | Multiple recipient support |
| `GET /api/bounces` | Bounce record retrieval |
| `DELETE /api/bounces` | Bounce record deletion |
| `GET/POST/DELETE /api/import/subscribers` | Bulk CSV import |
| `GET/POST/DELETE /api/media` | Media file management |
