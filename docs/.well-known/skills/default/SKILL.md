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

## API overview

### Configuration & Authentication

Point the client at your Listmonk instance and authenticate.

- `set_url_base`: Each Listmonk instance lives somewhere. This is where yours lives
- `get_base_url`: Each Listmonk instance lives somewhere. This is where yours lives
- `login`: Logs into Listmonk and stores that authentication for the life of your app
- `verify_login`: Call to verify that the stored auth token is still valid
- `is_healthy`: Checks that the token retrieved during login is still valid at your server

### Mailing Lists

Read and manage mailing lists.

- `lists`: Get mailing lists on the server
- `list_by_id`: Get the full details of a list with the given ID
- `create_list`: Create a new mailing list on the server
- `update_list`: Updates an existing mailing list on the server
- `delete_list`: Delete a specific list by its ID

### Subscribers

Create, query, update, and manage the status of subscribers.

- `subscribers`: Get a list of subscribers matching the criteria provided. If none, then all subscribers are returned
- `subscriber_by_email`: Retrieves the subscribe by email (e.g. "some_user@talkpython.fm")
- `subscriber_by_id`: Retrieves the subscribe by id (e.g. 201)
- `subscriber_by_uuid`: Retrieves the subscriber by uuid (e.g. "c37786af-e6ab-4260-9b49-740adpcm6ed")
- `create_subscriber`: Create a new subscriber on the Listmonk server
- `update_subscriber`: Update many aspects of a subscriber, from their email addresses and names, to custom attribute data, and
- `add_subscribers_to_lists`: Add a number of subscribers to a number of lists
- `enable_subscriber`: Set a subscriber's status to enable
- `disable_subscriber`: Set a subscriber's status to disable
- `block_subscriber`: Add a subscriber to the blocklist, AKA unsubscribe them
- `confirm_optin`: For opt-in situations, subscribers are added as unconfirmed first. This method will opt them in
- `delete_subscriber`: Completely delete a subscriber from your system (it's as if they were never there)

### Campaigns

Create, preview, update, and delete email campaigns.

- `campaigns`: Get campaigns on the server
- `campaign_by_id`: Get the full details of a campaign with the given ID
- `campaign_preview_by_id`: Get the preview of a campaign with the given ID
- `create_campaign`: Create a new campaign with the given parameters
- `update_campaign`: Update the given campaign with the provided campaign information
- `delete_campaign`: Completely delete a campaign from your system

### Templates

Manage email templates and set the default.

- `templates`: This function retrieves a list of all templates available in the system
- `template_by_id`: Retrieve a template by its ID
- `template_preview_by_id`: Get the preview of a template with the given ID
- `create_template`: Create a template with the specified details
- `update_template`: Update a template in the system
- `set_default_template`: Set the given template ID as the default template
- `delete_template`: Completely delete a template from your system

### Transactional Email

Send one-off transactional messages.

- `send_transactional_email`: Send a transactional email through Listmonk to the recipient

### Data Models

Pydantic models returned by and passed to the API functions.

- `models.MailingList`
- `models.SubscriberStatus`
- `models.SubscriberStatuses`
- `models.Subscriber`
- `models.CreateSubscriberModel`
- `models.Campaign`
- `models.CreateCampaignModel`
- `models.UpdateCampaignModel`
- `models.CampaignPreview`
- `models.Template`
- `models.CreateTemplateModel`
- `models.TemplatePreview`

### Exceptions

Errors raised by the client.

- `errors.ValidationError`
- `errors.OperationNotAllowedError`
- `errors.ListmonkFileNotFoundError`

## Resources

- [Full documentation](https://mkennedy.codes/docs/listmonk/)
- [llms.txt](llms.txt) — Indexed API reference for LLMs
- [llms-full.txt](llms-full.txt) — Comprehensive documentation for LLMs
- [Source code](https://github.com/mikeckennedy/listmonk)
