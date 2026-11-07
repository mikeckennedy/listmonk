# Errors and troubleshooting

Bad news arrives in two shapes in this library. Some calls raise. Others hand you a `False` or a `None` and expect you to look. Knowing which shape a call uses is the difference between a `try/except` that works and one that never fires.


# Calls that raise

Every data call checks the client state first and raises [listmonk.errors.OperationNotAllowedError](../reference/errors.OperationNotAllowedError.md#listmonk.errors.OperationNotAllowedError) if [`set_url_base()`](../reference/set_url_base.md) or a successful [`login()`](../reference/login.md) has not happened yet.

Bad arguments raise `ValueError` before any request is sent: an empty email in [create_subscriber()](../reference/create_subscriber.md#listmonk.create_subscriber), a template body without the `{ template "content" . }` placeholder, a list type that is not `public` or `private`, a campaign with no name or subject.

A 4xx or 5xx response from the server raises `httpx2.HTTPStatusError`. The exception carries the response, so `e.response.status_code` and `e.response.text` tell you what Listmonk said. Note the module name: this library uses [httpx2](https://github.com/pydantic/httpx2), the Pydantic-maintained fork of httpx, so catch `httpx2.HTTPStatusError`. An `httpx.HTTPStatusError` handler will not match.

An empty response body, or one that is not JSON (a proxy's HTML error page, say), raises [listmonk.errors.ValidationError](../reference/errors.ValidationError.md#listmonk.errors.ValidationError). [OperationNotAllowedError](../reference/errors.OperationNotAllowedError.md#listmonk.errors.OperationNotAllowedError) is a subclass of it, so one `except ValidationError` clause catches both.

A missing attachment path in [send_transactional_email()](../reference/send_transactional_email.md#listmonk.send_transactional_email) or [upload_media()](../reference/upload_media.md#listmonk.upload_media) raises [listmonk.errors.ListmonkFileNotFoundError](../reference/errors.ListmonkFileNotFoundError.md#listmonk.errors.ListmonkFileNotFoundError), a subclass of the built-in `FileNotFoundError`.


# Calls that return a value instead

| Call | Returns | When |
|----|----|----|
| [login()](../reference/login.md#listmonk.login), [is_healthy()](../reference/is_healthy.md#listmonk.is_healthy), [verify_login()](../reference/verify_login.md#listmonk.verify_login) | `False` | Credentials rejected, or the server unreachable. Never raises for these. |
| [confirm_optin()](../reference/confirm_optin.md#listmonk.confirm_optin), [add_subscribers_to_lists()](../reference/add_subscribers_to_lists.md#listmonk.add_subscribers_to_lists) | `False` | Any non-2xx response. [add_subscribers_to_lists()](../reference/add_subscribers_to_lists.md#listmonk.add_subscribers_to_lists) also returns `False` for empty inputs. |
| [subscriber_by_email()](../reference/subscriber_by_email.md#listmonk.subscriber_by_email), [subscriber_by_id()](../reference/subscriber_by_id.md#listmonk.subscriber_by_id), [subscriber_by_uuid()](../reference/subscriber_by_uuid.md#listmonk.subscriber_by_uuid), [campaign_by_id()](../reference/campaign_by_id.md#listmonk.campaign_by_id), [template_by_id()](../reference/template_by_id.md#listmonk.template_by_id) | `None` | Nothing matches. |
| [set_campaign_status()](../reference/set_campaign_status.md#listmonk.set_campaign_status), [start_campaign()](../reference/start_campaign.md#listmonk.start_campaign), [pause_campaign()](../reference/pause_campaign.md#listmonk.pause_campaign), [cancel_campaign()](../reference/cancel_campaign.md#listmonk.cancel_campaign) | `None` | No campaign has that ID. |
| [delete_subscriber()](../reference/delete_subscriber.md#listmonk.delete_subscriber), [delete_campaign()](../reference/delete_campaign.md#listmonk.delete_campaign), [delete_template()](../reference/delete_template.md#listmonk.delete_template), [test_campaign()](../reference/test_campaign.md#listmonk.test_campaign) | `False` | The target does not exist. |
| [update_subscriber()](../reference/update_subscriber.md#listmonk.update_subscriber), [update_campaign()](../reference/update_campaign.md#listmonk.update_campaign), [update_template()](../reference/update_template.md#listmonk.update_template) | `None` | The follow-up fetch after a successful update finds nothing. Rare. |

The odd one out is [`list_by_id()`](../reference/list_by_id.md), which returns a [MailingList](../reference/models.MailingList.md#listmonk.models.MailingList) rather than an optional and raises if the list is missing.

``` python
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
    ...  # the server answered with something that is not JSON

if subscriber is None:
    ...  # no such subscriber; not an error
```


# Timeouts

Every network call accepts `timeout_config`, an `httpx2.Timeout`, and defaults to 10 seconds. A slow or far-away instance, or a [subscribers()](../reference/subscribers.md#listmonk.subscribers) call that pages through a large list, may need more:

``` python
import httpx2

everyone = listmonk.subscribers(timeout_config=httpx2.Timeout(timeout=60))
```

A timeout surfaces as an `httpx2.TimeoutException` from the underlying request.


# OperationNotAllowedError: You must login before proceeding

Authentication is module-level state. Call `set_url_base(url)` and then `login(user, password)` once at startup, before any other function, and check that [login()](../reference/login.md#listmonk.login) returned `True`. A `False` return means the server rejected the credentials or could not be reached; no exception is raised in that case, which is why skipping the check leads here.

If your app runs under several worker processes, each process has its own copy of that state and each needs to log in. A fixture or startup hook is the usual place.


# Forbidden (403)

``` text
httpx2.HTTPStatusError: Client error '403 Forbidden' for url 'https://yoursite.local/api/subscribers?page=1&per_page=100&query=subscribers.email='john@example.com''
```

Your password was fine; a bad one makes [login()](../reference/login.md#listmonk.login) return `False` much earlier. The `query=` in the URL is the clue: this is a SQL-filtered subscriber lookup, and the API user's role lacks the `subscribers:sql_query` permission. Listmonk requires it whenever a `query` parameter is sent. Add the permission to the role in Users and Roles and retry. The [Listmonk roles documentation](https://listmonk.app/docs/roles-and-permissions/#user-roles) has the details.

Which calls need it: [`subscribers(query_text=...)`](../reference/subscribers.md), [`subscriber_by_email()`](../reference/subscriber_by_email.md), and [`subscriber_by_uuid()`](../reference/subscriber_by_uuid.md). Which do not: [`subscriber_by_id()`](../reference/subscriber_by_id.md), which uses Listmonk's direct per-subscriber endpoint, and `subscribers(list_id=...)` without a query.

A 403 from any other call means the role is missing the read or manage permission for that resource, or that the subscriber belongs to a list the API user may not see.


# test_campaign() raised 400: No known subscribers to test

Listmonk only sends campaign tests to addresses that already exist as subscribers. It does not create them, and when none of the addresses you passed are known it rejects the request with HTTP 400, which the client raises as `httpx2.HTTPStatusError`. Create the subscriber first (`create_subscriber(email, pre_confirm=True)`) or use an address that is already on a list. See [Campaigns](campaigns.md#test-before-you-send).


# Campaign status change rejected (400)

[start_campaign()](../reference/start_campaign.md#listmonk.start_campaign), [pause_campaign()](../reference/pause_campaign.md#listmonk.pause_campaign), and [cancel_campaign()](../reference/cancel_campaign.md#listmonk.cancel_campaign) ask the server for a specific transition, and Listmonk only allows some: draft to scheduled or running, scheduled to draft, running to paused or cancelled, paused to running. Starting a finished campaign or pausing a draft comes back as a 400. Read the campaign's `status` first if you are unsure where it is.


# HTTP 409 on create_subscriber()

The email already exists on the instance. Look the subscriber up with [subscriber_by_email()](../reference/subscriber_by_email.md#listmonk.subscriber_by_email) and update them instead; the [signup form recipe](recipes.md#handle-a-signup-form) shows the pattern.


# SSL certificate verification failed

httpx2 validates TLS certificates against the bundled `certifi` CA list by default. If you self-host Listmonk behind a custom or corporate Certificate Authority you may see:

``` text
ssl.SSLCertVerificationError: certificate verify failed: unable to get local issuer certificate
```

Point the client at your CA bundle through the standard environment variables before the library makes its first request:

``` bash
export SSL_CERT_FILE=/path/to/your-ca-bundle.pem   # or SSL_CERT_DIR=/path/to/ca-dir
```


# A transactional email returned True but never arrived

[send_transactional_email()](../reference/send_transactional_email.md#listmonk.send_transactional_email) returns `True` when Listmonk accepted the message for delivery. What happens after that (SMTP rejection, bounce, a messenger that is down) is reported in the Logs section of the Listmonk admin, not back to the client. Check there first, then the recipient's spam folder.
