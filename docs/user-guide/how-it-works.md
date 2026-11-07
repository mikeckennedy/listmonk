# How it works

Knowing what the client does on your behalf explains most of its behaviour, including the parts that look surprising at first.


# One module, one instance

`listmonk` keeps its configuration in four module-level variables: the base URL, the username, the password, and a logged-in flag. [`set_url_base()`](../reference/set_url_base.md) sets the first, [`login()`](../reference/login.md) sets the rest after validating the credentials against the health endpoint, and every other function checks the flag before doing anything and raises [OperationNotAllowedError](../reference/errors.OperationNotAllowedError.md#listmonk.errors.OperationNotAllowedError) if it is not set.

Two consequences follow. A process talks to one Listmonk instance at a time; to switch, call [set_url_base()](../reference/set_url_base.md#listmonk.set_url_base) and [login()](../reference/login.md#listmonk.login) again, and the new credentials are re-validated rather than trusted. And changing credentials is not thread-safe: do the configuration once at startup, before worker threads start, and leave it alone. Reads from worker threads are fine, since the variables never change after that.


# Every call is a fresh request

The client uses httpx2's module-level functions (`httpx2.get()`, `httpx2.post()`, and so on) rather than a long-lived `Client`. Each call opens its own connection, sends HTTP Basic auth built from the stored credentials, follows redirects, identifies itself with a `User-Agent` of the form `Listmonk-Client v0.7.33 / Python 3.14.0 / Darwin`, and times out after 10 seconds unless you pass `timeout_config`. There is no connection pooling and no session state, which is why a fake server for tests only needs to patch those four functions.

The trade-off is a little more latency per call. For a handful of calls per request in a web app it is unnoticeable; for a loop over tens of thousands of subscribers, batch where the API allows it ([add_subscribers_to_lists()](../reference/add_subscribers_to_lists.md#listmonk.add_subscribers_to_lists) takes many IDs at once) and pull data in bulk with [subscribers()](../reference/subscribers.md#listmonk.subscribers) rather than one lookup at a time.


# Pagination

[`subscribers()`](../reference/subscribers.md) asks for 500 records per page and keeps going until the server's `total` is reached, so one call can be several requests. [`lists()`](../reference/lists.md), [`campaigns()`](../reference/campaigns.md), and [`templates()`](../reference/templates.md) ask for one very large page and make a single request.


# Lookups by email and UUID are SQL filters

Listmonk has a direct endpoint for fetching a subscriber by ID, and [`subscriber_by_id()`](../reference/subscriber_by_id.md) uses it. It has no direct endpoint for email or UUID, so [`subscriber_by_email()`](../reference/subscriber_by_email.md) and [`subscriber_by_uuid()`](../reference/subscriber_by_uuid.md) send a `query` parameter that Listmonk runs as a SQL expression inside a read-only transaction. That is why those two need the `subscribers:sql_query` permission, and why the client quotes the value as a SQL literal with embedded quotes escaped before sending it.


# Models

Responses are parsed into Pydantic models in `listmonk.models`: [`Subscriber`](../reference/models.Subscriber.md), [`MailingList`](../reference/models.MailingList.md), [`Campaign`](../reference/models.Campaign.md), [`Template`](../reference/models.Template.md), and [`Media`](../reference/models.Media.md), plus the enums [`SubscriberStatuses`](../reference/models.SubscriberStatuses.md) and [`CampaignStatuses`](../reference/models.CampaignStatuses.md). Fields the server may omit are `Optional`. Timestamps are `datetime` objects.

The update functions do not send those response models back as-is. [update_subscriber()](../reference/update_subscriber.md#listmonk.update_subscriber) builds a [CreateSubscriberModel](../reference/models.CreateSubscriberModel.md#listmonk.models.CreateSubscriberModel) from the fields Listmonk's PUT accepts, [update_campaign()](../reference/update_campaign.md#listmonk.update_campaign) builds an [UpdateCampaignModel](../reference/models.UpdateCampaignModel.md#listmonk.models.UpdateCampaignModel) (which is where a past `send_at` gets dropped), and [update_template()](../reference/update_template.md#listmonk.update_template) builds a [CreateTemplateModel](../reference/models.CreateTemplateModel.md#listmonk.models.CreateTemplateModel). Those request models are public too, in case you want to see exactly what goes over the wire.


# Response validation

Every JSON call runs the response through one helper: raise `httpx2.HTTPStatusError` for a 4xx or 5xx, raise [ValidationError](../reference/errors.ValidationError.md#listmonk.errors.ValidationError) for an empty body or a body that is not JSON, otherwise hand back the parsed dict. Previews are the exception, since Listmonk returns them as raw HTML.


# What the client does not cover

Listmonk's API is larger than this client. Not wrapped, as of this version: campaign analytics, campaign archives, bounces, bulk subscriber deletion and blocklisting by query, listing and deleting media, importing subscribers from files, settings, and user management. Transactional sends by subscriber ID (rather than email) are also not exposed. For any of those, call the [Listmonk API](https://listmonk.app/docs/apis/apis/) directly with httpx2 and the same Basic auth; the base URL and credentials you gave the client are available as [listmonk.get_base_url()](../reference/get_base_url.md#listmonk.get_base_url) and the `username` and `password` attributes of `listmonk.impl`.

An async variant is planned but not yet implemented. With httpx2 underneath, the shape of it is clear; it is a matter of doing the work.


# Version and user agent

`listmonk.__version__` reports the installed package version, read from the package metadata, and `listmonk.user_agent` is the string sent with every request.
