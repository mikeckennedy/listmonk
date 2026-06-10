## subscriber_by_uuid()


Retrieve a single subscriber by their UUID (e.g. "c37786af-e6ab-4260-9b49-740adpcm6ed").


Usage

``` python
subscriber_by_uuid(
    subscriber_uuid,
    timeout_config=None,
)
```


The UUID is matched against `subscribers.uuid` on the server and the first matching subscriber is returned.


## Parameters


`subscriber_uuid: str`  
UUID of the subscriber to look up (e.g. "c37786af-e6ab-4260-9b49-740adpcm6ed").

`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`Optional[models.Subscriber]`  
The matching models.Subscriber, or None if no subscriber has that UUID.


## Raises


`OperationNotAllowedError`  
If the base URL has not been set or you have not logged in.

`ValidationError`  
If the server returns an empty body or invalid JSON.

`httpx2.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.
