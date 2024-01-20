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

## Installation

Just `pip install listmonk`


## Usage

```python
...
```

