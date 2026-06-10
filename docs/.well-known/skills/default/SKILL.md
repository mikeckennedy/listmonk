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

Create, preview, update, and delete email campaigns.

- `campaigns`: Get all campaigns on the server
- `campaign_by_id`: Get the full details of a campaign with the given ID
- `campaign_preview_by_id`: Get the rendered preview of a campaign with the given ID
- `create_campaign`: Create a new campaign with the given parameters
- `update_campaign`: Update an existing campaign with the provided campaign information
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

## Resources

- [Full documentation](https://mkennedy.codes/docs/listmonk/)
- [llms.txt](llms.txt) — Indexed API reference for LLMs
- [llms-full.txt](llms-full.txt) — Comprehensive documentation for LLMs
- [Source code](https://github.com/mikeckennedy/listmonk)
