# Listmonk Email API Client for Python

Somewhere in your app, a person just clicked "Sign up". A welcome email has to leave the building, a newsletter needs them on the right list, and next Tuesday they will forget their password. [Listmonk](https://listmonk.app) is the open source, self-hosted mail platform that handles all of that. This package is how your Python code talks to it.

`listmonk` is built on [httpx2](https://github.com/pydantic/httpx2) and [pydantic](https://pydantic.dev) and is meant for wiring a Listmonk instance into your web app. The [Listmonk API is extensive](https://listmonk.app/docs/apis/apis/); this client deliberately covers the subset most apps need day to day: subscribe, unsubscribe, segment people into lists, send the one-off emails your app depends on, and run campaigns.

It does not cover every endpoint yet. Campaign analytics and bulk subscriber deletion, for example, are not implemented. If you need one of those, open an issue first and then send a PR; they are welcome.

🔀 Async is planned but not yet implemented. With httpx2 underneath, it should be a small step when the time comes.

## Documentation

📚 Full documentation lives at **[mkennedy.codes/docs/listmonk](https://mkennedy.codes/docs/listmonk/)**, including the complete [API Reference](https://mkennedy.codes/docs/listmonk/reference/) for every function, model, and exception in the library.

🤖 Using a coding agent? Point it at the [Agent Skill](https://mkennedy.codes/docs/listmonk/skills.html) (a cheat sheet of the rules of this package) or at [llms-full.txt](https://mkennedy.codes/docs/listmonk/llms-full.txt), which holds every signature and docstring in one file.

## Core Features

- ➕ **Add a subscriber** to your subscribed users.
- 🙎 Get **subscriber details** by email, ID, UUID, and more.
- 📝 **Modify subscriber details** (including custom attribute collection).
- 🔍 **Search** your users based on app and custom attributes.
- 🏥 Check the **health and connectivity** of your instance.
- 👥 Retrieve your **segmentation lists**, list details, and subscribers.
- 🙅 Unsubscribe and block users who don't want to be contacted further.
- 💥 Completely delete a subscriber from your instance.
- 📧 Send transactional email with template data (e.g. password reset emails), including to people who are not subscribers.
- 📨 Manage campaign (bulk) emails from the API: create, preview, test, send, pause, and cancel them.
- 📎 Upload media and attach files to campaigns.
- 🎨 Edit and create templates to control the overall look and feel of campaigns.
- 📝 Create, edit and delete lists.
- ✅ Fully type annotated and ships `py.typed`, so mypy/pyright type checking works out of the box.

## Installation

Just `pip install listmonk` (or `uv add listmonk`). You need two things from your Listmonk instance: its address, and an API user. Recent Listmonk versions want you to create a dedicated API user with a token under Users rather than reusing your own login, and the role you give that user decides what the calls below are allowed to do.

## Usage: a tour in seven scenes

Meet Jane. She has just signed up for your app. Over the next few scenes she will get onto a couple of lists, receive a password reset, be sent a newsletter, and eventually (sorry, Jane) be deleted. Each scene builds on the one before, and by the end you will have touched most of the library.

### Scene 1: Knock on the door

Everything starts with two calls: where the server is, and who you are. Authentication is stored at module level, so you do this once at startup and every later call reuses it. Note that `login()` answers with a bool rather than an exception; a `False` means the server said no, or could not be reached at all.

```python

import pathlib
import listmonk
from listmonk.models import MailingList, Subscriber
from typing import Optional

listmonk.set_url_base('https://yourlistmonkurl.com')

listmonk.login('sammy_z', '1234')
valid: bool = listmonk.verify_login()

# Is it alive and working?
up: bool = listmonk.is_healthy()
```

### Scene 2: The guest lists

Lists are how Listmonk segments people: the newsletter, the beta testers, the folks who bought the advanced course. You can create and reshape them from code, or just read the ones already set up in the admin UI.

```python
# Create, update, and delete lists
new_list: MailingList = listmonk.create_list(list_name="my_new_list")
listmonk.update_list(list_id=new_list.id, description='Updated description')
listmonk.delete_list(new_list.id)

# Read data about your lists
lists: list[MailingList] = listmonk.lists()
the_list: MailingList = listmonk.list_by_id(list_id=7)
```

### Scene 3: Jane signs up

Creating a subscriber is one call. `pre_confirm=True` tells Listmonk that your app already handled consent, so no double opt-in email goes out. The `attribs` dict is a free-form bag of custom data (a plan name, a signup source, a rating) that you can query later. Once Jane exists you can find her again by email, ID, or UUID; each of those returns `None` rather than raising when nobody matches.

```python
# Various ways to access existing subscribers
subscribers: list[Subscriber] = listmonk.subscribers(list_id=9)

subscriber: Optional[Subscriber] = listmonk.subscriber_by_email('testuser@some.domain')
subscriber: Optional[Subscriber] = listmonk.subscriber_by_id(2001)
subscriber: Optional[Subscriber] = listmonk.subscriber_by_uuid('f6668cf0-1c...')

# Create a new subscriber
new_subscriber = listmonk.create_subscriber(
    'testuser@some.domain', 'Jane Doe',
    {1, 7, 9}, pre_confirm=True, attribs={...})
```

Updates follow one pattern throughout the library: fetch the model, change what you like, pass it back. The client sends the whole record and returns the server's fresh copy. List membership is worked out as "what she has now, minus the removals, plus the additions". Her global status (enabled, disabled, or blocklisted) stays whatever it already was unless you say otherwise.

```python
# Change the email, custom rating, and add to lists 4 & 6, remove from 5.
subscriber.email = 'newemail@some.domain'
subscriber.attribs['rating'] = 7
subscriber = listmonk.update_subscriber(subscriber, {4, 6}, {5})

# Bulk-add existing subscribers to lists in one call
listmonk.add_subscribers_to_lists([2001, 2002], [4, 6])

# Confirm single-opt-ins via the API (e.g. for when you manage that on your platform)
listmonk.confirm_optin(subscriber.uuid, the_list.uuid)
```

### Scene 4: Jane changes her mind

People pause, people leave, and occasionally people ask to be forgotten entirely. Those are three different operations and it matters which one you reach for. Disabling pauses delivery and is reversible. Blocking is the proper unsubscribe: Jane's record stays, so she can never be accidentally re-added by an import, but nothing is ever sent to her again. Deleting erases her as if she had never existed.

```python
# Disable then re-enable a subscriber
subscriber = listmonk.disable_subscriber(subscriber)
subscriber = listmonk.enable_subscriber(subscriber)

# Block (unsubscribe) them
listmonk.block_subscriber(subscriber)

# Fully delete them from your system
listmonk.delete_subscriber(subscriber.email)
```

### Scene 5: The password reset that cannot wait

Campaigns go to lists. Transactional email goes to one person, right now, because something just happened: a reset code, a receipt, an invite. You write a `tx` template in Listmonk once, then send it with the data that fills in the blanks. Listmonk templates are Go templates, so the merge data shows up in the template as `{{ .Tx.Data.reset_code }}`, not Jinja.

```python
# Send an individual, transactional email (e.g. password reset)
to_email = 'testuser@some.domain'
from_email = 'app@your.domain'
template_id = 3  # *TX* template ID from listmonk
template_data = {'full_name': 'Test User', 'reset_code': 'abc123'}

status: bool = listmonk.send_transactional_email(
    to_email, template_id, from_email=from_email,
    template_data=template_data, content_type='html')

# Optional plaintext fallback for multipart HTML emails.
status = listmonk.send_transactional_email(
    to_email,
    template_id,
    from_email=from_email,
    template_data=template_data,
    content_type='html',
    altbody='Plaintext order summary for mail clients that prefer text.'
)

# You can also add one or multiple attachments with transactional mails
attachments = [
    pathlib.Path("/path/to/your/file1.pdf"),
    pathlib.Path("/path/to/your/file2.png")
]

status: bool = listmonk.send_transactional_email(
    to_email,
    template_id,
    from_email=from_email,
    template_data=template_data,
    attachments=attachments,
    content_type='html',
    altbody='Plaintext fallback body'
)
```

Here is the twist. By default Listmonk will only send a transactional email to someone who is already a subscriber. That is fine for Jane, but what about the colleague she just invited, who has no account yet? Pass `subscriber_mode='external'` and Listmonk skips the lookup and sends to anyone. The price is that only `{{ .Subscriber.Email }}` is available inside the template, so anything else it needs has to ride along in `template_data`.

```python
# By default the recipient must already be a subscriber. To email anyone at all
# (password resets, invites, receipts) use subscriber_mode='external'; in that mode
# only {{ .Subscriber.Email }} is available in the template, so pass everything
# else via template_data and read it as {{ .Tx.Data.<key> }}.
listmonk.send_transactional_email(
    'stranger@some.domain', template_id,
    subscriber_mode='external', template_data={'name': 'Sam', 'reset_code': 'abc123'})

# Several recipients in one call: pass a list of addresses instead of one string.
listmonk.send_transactional_email(
    ['one@some.domain', 'two@some.domain'], template_id, subscriber_mode='external')
```

### Scene 6: The newsletter

Now for the bulk send. A campaign is a message aimed at one or more lists, and it has a life cycle: it is born a draft, it can be scheduled, it runs, it can be paused, and it ends up finished or cancelled. The single most useful thing to know is that creating a campaign does not send it. That is a separate, deliberate step, and there is a test send in between so you can read it in your own inbox first.

Attachments for campaigns are a two-step dance: upload the file to Listmonk's media library, then reference its ID. A default Listmonk install only accepts image extensions in the media library, which you can widen in its settings.

```python
# Access existing campaigns
from listmonk.models import Campaign
from datetime import datetime, timedelta

campaigns: list[Campaign] = listmonk.campaigns()
campaign: Optional[Campaign] = listmonk.campaign_by_id(15)

# Upload media and create a campaign with attachments. A default Listmonk install only
# accepts image extensions here; widen Settings > Media > Upload extensions for others.
media = listmonk.upload_media(pathlib.Path("/path/to/chart.png"))
# Or upload from bytes: media = listmonk.upload_media(png_bytes, filename="chart.png")

listmonk.create_campaign(name='This is my Great Campaign!',
                         subject="You won't believe this!",
                         body='<p>Some Insane HTML!</p>',  # Optional
                         alt_body='Some Insane TXT!',  # Optional
                         send_at=datetime.now() + timedelta(hours=1),  # Optional
                         template_id=5,  # Optional; defaults to None (server uses its default template)
                         list_ids={1, 2},  # Optional Defaults to 1
                         tags=['good', 'better', 'best'],  # Optional
                         media_ids=[media.id],  # Optional, attach uploaded media
                         )

# Update A Campaign
campaign_to_update: Optional[Campaign] = listmonk.campaign_by_id(15)
campaign_to_update.name = "More Elegant Name"
campaign_to_update.subject = "Even More Clickbait!!"
campaign_to_update.body = "<p>There's a lot more we need to say so we're updating this programmatically!"
campaign_to_update.altbody = "There's a lot more we need to say so we're updating this programmatically!"
campaign_to_update.lists = [3, 4]

# Existing attachments are kept on update; pass media_ids=[...] to change them
# (or media_ids=[] to remove them all).
listmonk.update_campaign(campaign_to_update)

# Preview Campaign
preview = listmonk.campaign_preview_by_id(15)
print(preview.preview)
```

The send itself goes through Listmonk's dedicated status endpoint, which is why `update_campaign()` cannot start a campaign no matter what you set `status` to. Test first (every test address must already be a subscriber, or the server refuses with a 400), then start.

```python
# Creating a campaign does not send it. Send a test copy to yourself first (each
# address must already be a subscriber), then start it. update_campaign() cannot
# change the status; these calls use Listmonk's dedicated status endpoint.
listmonk.test_campaign(15, ['you@your.domain'])
listmonk.start_campaign(15)   # draft -> running; the same as set_campaign_status(15, CampaignStatuses.running)
listmonk.pause_campaign(15)   # running -> paused; resume with start_campaign()
listmonk.cancel_campaign(15)  # stop for good

# Delete a Campaign (by its numeric ID)
listmonk.delete_campaign(15)
```

### Scene 7: Dressing it up

Templates are the frame around every message: the header, the footer, the brand colours. There are two kinds, `campaign` and `tx`, and both have one hard rule. The body must contain `{{ template "content" . }}` exactly where the message goes, or the client refuses to create it before a single byte reaches the server.

```python
# Access existing Templates
from listmonk.models import Template
templates: list[Template] = listmonk.templates()
template: Template = listmonk.template_by_id(2)

# Create a new Template for Campaigns
new_template = listmonk.create_template(
    name='NEW TEMPLATE',
    body='<p>Some Insane HTML! {{ template "content" . }} </p>',
    type='campaign',
)

# Update A Template
new_template.name = "Bob's Great Template"
listmonk.update_template(new_template)

# Mark a template as the default for its type
listmonk.set_default_template(new_template.id)

# Delete a Template
listmonk.delete_template(3)

# Preview Template
preview = listmonk.template_preview_by_id(3)
print(preview.preview)

# Create a new template for Transactional Emails
# (the {{ template "content" . }} placeholder is required in every template body)
new_tx_template = listmonk.create_template(
    name='NEW TX TEMPLATE',
    subject='Your Transactional Email Subject',
    body='<p>Hi {{ .Subscriber.FirstName }}! {{ template "content" . }}</p>',
    type='tx',
)
```

That is the whole tour. Jane has been welcomed, segmented, reset, newslettered, and deleted, and you have seen every corner of the library that matters. The rest of this page is about what happens when something goes wrong.

## Error handling

Bad news arrives in two shapes in this library, and it pays to know which shape a call uses before you wrap it in `try/except`. Some calls raise. Others hand you a `False` or a `None` and expect you to look.

**Calls that raise.** Every data call first checks the client state and raises `listmonk.errors.OperationNotAllowedError` if `set_url_base()` or a successful `login()` has not happened yet. Bad arguments (an empty email, a template body without the `{{ template "content" . }}` placeholder, an unknown list type) raise `ValueError` before any request is sent. A 4xx or 5xx response raises `httpx2.HTTPStatusError`, and an empty or non-JSON response body raises `listmonk.errors.ValidationError`. Note the module name: this library uses [httpx2](https://github.com/pydantic/httpx2), so catch `httpx2.HTTPStatusError`, not `httpx.HTTPStatusError`.

**Calls that return a value instead.** `login()`, `is_healthy()`, and `verify_login()` return `False` when the credentials are rejected or the server cannot be reached; they never raise for those cases. `confirm_optin()` and `add_subscribers_to_lists()` return `False` on a non-2xx response. The single-item lookups (`subscriber_by_email()`, `subscriber_by_id()`, `subscriber_by_uuid()`, `campaign_by_id()`, `template_by_id()`) return `None` when nothing matches, as do `set_campaign_status()` and its `start`/`pause`/`cancel` wrappers for an unknown campaign ID. `delete_subscriber()`, `delete_campaign()`, `delete_template()`, and `test_campaign()` return `False` when the target does not exist.

```python
import httpx2
import listmonk
from listmonk.errors import OperationNotAllowedError, ValidationError

try:
    subscriber = listmonk.subscriber_by_email('someone@some.domain')
except OperationNotAllowedError:
    ...  # call set_url_base() and login() first
except httpx2.HTTPStatusError as e:
    ...  # e.response.status_code, e.response.text
except ValidationError:
    ...  # the server answered with something that is not JSON (a proxy error page, say)

if subscriber is None:
    ...  # no such subscriber; not an error
```

Every network call accepts an optional `timeout_config`, an `httpx2.Timeout`, and defaults to 10 seconds. Pass a longer one for slow or self-hosted instances, for example `listmonk.subscribers(timeout_config=httpx2.Timeout(timeout=60))`.

## F.A.Q.

### I got OperationNotAllowedError: You must login before proceeding

Authentication is module-level state. Call `listmonk.set_url_base(url)` and then `listmonk.login(user, password)` once at startup, before any other function, and check that `login()` returned `True`. A `False` return means the server rejected the credentials or could not be reached; no exception is raised in that case.

### I got httpx2.HTTPStatusError: Client error '403 Forbidden'

If you encounter an error like this in your console:

```text
httpx2.HTTPStatusError: Client error '403 Forbidden' for url 'https://yoursite.local/api/subscribers?page=1&per_page=100&query=subscribers.email='john@example.com''
```

It means the authenticated user doesn’t have sufficient permissions to run SQL queries on subscriber data. Your password was fine (a bad one makes `login()` return `False` much earlier); it is the role that is missing something.

**Solution:** Check the role assigned to your user. It must include the `subscribers:sql_query` permission to allow executing SQL queries on subscriber data. You can review and update user roles in your system’s admin panel. [[Reference](https://listmonk.app/docs/roles-and-permissions/#user-roles)] `subscriber_by_email()` and `subscriber_by_uuid()` use this same query mechanism, so they need the permission too. `subscriber_by_id()` and `subscribers(list_id=...)` do not.

### test_campaign() raised 400 Bad Request: No known subscribers to test

Listmonk only sends campaign tests to addresses that already exist as subscribers. It does not create them, and when none of the addresses you passed are known it rejects the request with HTTP 400, which the client raises as `httpx2.HTTPStatusError`. Create the subscriber first (`create_subscriber(email, pre_confirm=True)`) or use an address that is already on a list.

### I got an SSL certificate verification error against my self-hosted Listmonk

[httpx2](https://github.com/pydantic/httpx2) validates TLS certificates against the bundled `certifi` CA list by default. If you self-host Listmonk behind a custom or corporate Certificate Authority you may see an error like:

```text
ssl.SSLCertVerificationError: certificate verify failed: unable to get local issuer certificate
```

**Solution:** Point the client at your CA bundle via the standard environment variables before using the library:

```bash
export SSL_CERT_FILE=/path/to/your-ca-bundle.pem   # or SSL_CERT_DIR=/path/to/ca-dir
```

## Want to contribute?

PRs are welcome. But please open an issue first to see if the proposed feature fits with the direction of this library.

Enjoy.
