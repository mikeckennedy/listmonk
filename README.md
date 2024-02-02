# Listmonk Email App API Client for Python

Client for the for open source, self-hosted [Listmonk email platform](https://listmonk.app) based on 
[httpx](https://www.python-httpx.org) and [pydantic](https://pydantic.dev).  

`listmonk` is intended for integrating your Listmonk instance into your web app. The [Listmonk API is extensive](https://listmonk.app/docs/apis/apis/) but this only covers the subset that most developers will need for common SaaS actions such as subscribe, unsubscribe, and segmentate users (into separate lists).

So while it doesn't currently cover every endpoint (for example you cannot create a list programatically nor can you edit HTML templates for campaigns over APIs) it will likely work for you. That said, PRs are weclome.

🔀 Async is currently planned but not yet implemented. With the httpx-base, it should be trivial if needed.

## Core Features

* ➕**Add a subscriber** to your subscribed users. 
* 🙎 Get **subscriber details** by email, ID, UUID, and more.
* 📝 **Modify subscriber details** (including custom attribute collection).
* 🔍 **Search** your users based on app and custom attributes.
* 🏥 Check the **health and connectivity** of your instance.
*  👥 Retrieve your **segmentation lists**,  list details, and subscribers.
* 🙅 Unsubscribe and block users who don't want  to be contacted further.
* 💥 Completely delete a subscriber from your instance.
* 📧 Send transactional email with template data (e.g. password reset emails).

## Installation

Just `pip install listmonk`


## Usage

```python

import pathlib
import listmonk

listmonk.set_url_base('https://yourlistmonkurl.com')

listmonk.login('sammy_z', '1234')
valid: bool = listmonk.verify_login()

# Is it alive and working?
up: bool = listmonk.is_healthy()

# Read data about your lists
lists: list[] = listmonk.lists()
the_list: MailingList = listmonk.list_by_id(list_id=7)

# Various ways to access existing subscribers
subscribers: list[] = listmonk.subscribers(list_id=9)

subscriber: Subscriber = listmonk.subscriber_by_email('testuser@some.domain')
subscriber: Subscriber = listmonk.subscriber_by_id(2001)
subscriber: Subscriber = listmonk.subscriber_by_uuid('f6668cf0-1c...')

# Create a new subscriber
new_subscriber = listmonk.create_subscriber(
           'testuser@some.domain', 'Jane Doe',
            {1, 7, 9}, pre_confirm=True, attribs={...} )

# Change the email, custom rating, and add to lists 4 & 6, remove from 5.
subscriber.email = 'newemail@some.domain'
subscriber.attribs['rating'] = 7
subscriber = listmonk.update_subscriber(subscriber, {4, 6}, {5})

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
    content_type='html'
)
```

## Want to contribute?

PRs are welcome. But please open an issue first to see if the proposed feature fits with the direction of this library.

Enjoy.
