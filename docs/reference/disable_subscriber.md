## disable_subscriber()


Set a subscriber's status to disabled, pausing their subscription so they will not receive campaigns.


Usage

``` python
disable_subscriber(
    subscriber,
    timeout_config=None,
)
```


This is a convenience wrapper around update_subscriber that changes only the status.


## Parameters


`subscriber: models.Subscriber`  
The subscriber to disable. Must have a valid id.

`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`Optional[models.Subscriber]`  
The refreshed subscriber object from the server, or None if the subscriber can no longer be found.


## Raises


`ValueError`  
If subscriber is None or has no id.

`OperationNotAllowedError`  
If the base URL is not set or you are not logged in.

`httpx2.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.

`ValidationError`  
If the follow-up fetch returns an empty or invalid JSON response.
