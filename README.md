# Listmonk Email API Client for Python

Client for the open source, self-hosted [Listmonk email platform](https://listmonk.app) based on
[httpx2](https://github.com/pydantic/httpx2) and [pydantic](https://pydantic.dev).

`listmonk` is intended for integrating your Listmonk instance into your web app. The [Listmonk API is extensive](https://listmonk.app/docs/apis/apis/) but this only covers the subset that most developers will need for common SaaS actions such as subscribe, unsubscribe, and segment users (into separate lists).

So while it doesn't currently cover every endpoint (for example campaign analytics and bulk subscriber deletion are not yet implemented) it will likely work for you. That said, PRs are welcome.

🔀 Async is currently planned but not yet implemented. With the httpx2-base, it should be trivial if needed.

## Documentation

📚 Full documentation lives at **[mkennedy.codes/docs/listmonk](https://mkennedy.codes/docs/listmonk/)**, including the complete [API Reference](https://mkennedy.codes/docs/listmonk/reference/) for every function, model, and exception in the library.

## Core Features

- ➕**Add a subscriber** to your subscribed users.
- 🙎 Get **subscriber details** by email, ID, UUID, and more.
- 📝 **Modify subscriber details** (including custom attribute collection).
- 🔍 **Search** your users based on app and custom attributes.
- 🏥 Check the **health and connectivity** of your instance.
- 👥 Retrieve your **segmentation lists**, list details, and subscribers.
- 🙅 Unsubscribe and block users who don't want to be contacted further.
- 💥 Completely delete a subscriber from your instance.
- 📧 Send transactional email with template data (e.g. password reset emails).
- 📨 Manage campaign (bulk) emails from the API.
- 🎨 Edit and create templates to control the overall look and feel of campaigns.
- 📝 Create, edit and delete lists.
- ✅ Fully type annotated and ships `py.typed`, so mypy/pyright type checking works out of the box.

## Installation

Just `pip install listmonk`

## Usage

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

# Create, update, and delete lists
new_list: MailingList = listmonk.create_list(list_name="my_new_list")
listmonk.update_list(list_id=new_list.id, description='Updated description')
listmonk.delete_list(new_list.id)

# Read data about your lists
lists: list[MailingList] = listmonk.lists()
the_list: MailingList = listmonk.list_by_id(list_id=7)

# Various ways to access existing subscribers
subscribers: list[Subscriber] = listmonk.subscribers(list_id=9)

subscriber: Optional[Subscriber] = listmonk.subscriber_by_email('testuser@some.domain')
subscriber: Optional[Subscriber] = listmonk.subscriber_by_id(2001)
subscriber: Optional[Subscriber] = listmonk.subscriber_by_uuid('f6668cf0-1c...')

# Create a new subscriber
new_subscriber = listmonk.create_subscriber(
    'testuser@some.domain', 'Jane Doe',
    {1, 7, 9}, pre_confirm=True, attribs={...})

# Change the email, custom rating, and add to lists 4 & 6, remove from 5.
subscriber.email = 'newemail@some.domain'
subscriber.attribs['rating'] = 7
subscriber = listmonk.update_subscriber(subscriber, {4, 6}, {5})

# Bulk-add existing subscribers to lists in one call
listmonk.add_subscribers_to_lists([2001, 2002], [4, 6])

# Confirm single-opt-ins via the API (e.g. for when you manage that on your platform)
listmonk.confirm_optin(subscriber.uuid, the_list.uuid)

# Disable then re-enable a subscriber
subscriber = listmonk.disable_subscriber(subscriber)
subscriber = listmonk.enable_subscriber(subscriber)

# Block (unsubscribe) them
listmonk.block_subscriber(subscriber)

# Fully delete them from your system
listmonk.delete_subscriber(subscriber.email)

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

# Access existing campaigns
from listmonk.models import Campaign
from datetime import datetime, timedelta

campaigns: list[Campaign] = listmonk.campaigns()
campaign: Optional[Campaign] = listmonk.campaign_by_id(15)

# Create a new Campaign
listmonk.create_campaign(name='This is my Great Campaign!',
                         subject="You won't believe this!",
                         body='<p>Some Insane HTML!</p>',  # Optional
                         alt_body='Some Insane TXT!',  # Optional
                         send_at=datetime.now() + timedelta(hours=1),  # Optional
                         template_id=5,  # Optional; defaults to None (server uses its default template)
                         list_ids={1, 2},  # Optional Defaults to 1
                         tags=['good', 'better', 'best']  # Optional
                         )

# Update A Campaign
campaign_to_update: Optional[Campaign] = listmonk.campaign_by_id(15)
campaign_to_update.name = "More Elegant Name"
campaign_to_update.subject = "Even More Clickbait!!"
campaign_to_update.body = "<p>There's a lot more we need to say so we're updating this programmatically!"
campaign_to_update.altbody = "There's a lot more we need to say so we're updating this programmatically!"
campaign_to_update.lists = [3, 4]

listmonk.update_campaign(campaign_to_update)

# Delete a Campaign (by its numeric ID)
listmonk.delete_campaign(15)

# Preview Campaign
preview = listmonk.campaign_preview_by_id(15)
print(preview.preview)

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

## F.A.Q.

### I got httpx2.HTTPStatusError: Client error '403 Forbidden'

If you encounter an error like this in your console:

```text
httpx2.HTTPStatusError: Client error '403 Forbidden' for url 'https://yoursite.local/api/subscribers?page=1&per_page=100&query=subscribers.email='john@example.com''
```

It means the authenticated user doesn’t have sufficient permissions to run SQL queries on subscriber data.

**Solution:** Check the role assigned to your user. It must include the `subscribers:sql_query` permission to allow executing SQL queries on subscriber data. You can review and update user roles in your system’s admin panel. [[Reference](https://listmonk.app/docs/roles-and-permissions/#user-roles)]

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
