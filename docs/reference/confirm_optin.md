## confirm_optin()


Confirm a subscriber's opt-in to a list via the API.


Usage

``` python
confirm_optin(
    subscriber_uuid,
    list_uuid,
    timeout_config=None,
)
```


For opt-in lists, subscribers are added as unconfirmed first. Call this to opt them in, but only when they are genuinely opting in (for example, from your own opt-in form handled in your code). This submits the public opt-in form on the subscription endpoint rather than calling a JSON API, so HTTP errors are reported as a False return value rather than raised.


## Parameters


`subscriber_uuid: Optional[str]`  
The Subscriber.uuid value for the subscriber. Must be non-empty.

`list_uuid: Optional[str]`  
The MailingList.uuid value for the list. Must be non-empty.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`bool`  
True if the opt-in succeeded, False if the server responded with a non-success status.


## Raises


`ValueError`  
If subscriber_uuid or list_uuid is empty.

`OperationNotAllowedError`  
If the base URL is not set or you are not logged in.
