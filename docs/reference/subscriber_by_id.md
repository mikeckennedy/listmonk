## subscriber_by_id()


Retrieve a single subscriber by their numeric Listmonk ID (e.g. 201).


Usage

``` python
subscriber_by_id(
    subscriber_id,
    timeout_config=None,
)
```


The ID is matched against `subscribers.id` on the server and the first matching subscriber is returned.


## Parameters


`subscriber_id: int`  
Numeric ID of the subscriber to look up (e.g. 201).

`timeout_config: Optional[httpx.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`Optional[models.Subscriber]`  
The matching models.Subscriber, or None if no subscriber has that ID.


## Raises


`OperationNotAllowedError`  
If the base URL has not been set or you have not logged in.

`ValidationError`  
If the server returns an empty body or invalid JSON.

`httpx.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.
