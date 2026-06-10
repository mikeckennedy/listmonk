## subscriber_by_email()


Retrieve a single subscriber by their email address (e.g. "some_user@talkpython.fm").


Usage

``` python
subscriber_by_email(
    email,
    timeout_config=None,
)
```


The email is matched exactly against `subscribers.email` on the server (a `+` in the address is URL-encoded automatically), and the first matching subscriber is returned.


## Parameters


`email: str`  
Email address of the subscriber to look up (e.g. "some_user@talkpython.fm").

`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`Optional[models.Subscriber]`  
The matching models.Subscriber, or None if no subscriber has that email.


## Raises


`OperationNotAllowedError`  
If the base URL has not been set or you have not logged in.

`ValidationError`  
If the server returns an empty body or invalid JSON.

`httpx2.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.
