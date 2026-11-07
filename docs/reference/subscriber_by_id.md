## subscriber_by_id()


Retrieve a single subscriber by their numeric Listmonk ID (e.g. 201).


Usage

``` python
subscriber_by_id(
    subscriber_id,
    timeout_config=None,
)
```


This uses Listmonk's direct `GET /api/subscribers/{id}` endpoint, so unlike subscriber_by_email() and subscriber_by_uuid() it does not need the `subscribers:sql_query` permission. Listmonk answers an unknown ID with HTTP 400, which is reported here as None rather than raised.


## Parameters


`subscriber_id: int`  
Numeric ID of the subscriber to look up (e.g. 201).

`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`Optional[models.Subscriber]`  
The matching models.Subscriber, or None if no subscriber has that ID.


## Raises


`OperationNotAllowedError`  
If the base URL has not been set or you have not logged in.

`ValidationError`  
If the server returns an empty body or invalid JSON.

`httpx2.HTTPStatusError`  
If the server responds with a 4xx or 5xx status other than the 400 it uses for an unknown ID (for example a 403 when the API user may not read that subscriber's lists).


## Examples

``` python
>>> import listmonk
>>> sub = listmonk.subscriber_by_id(201)
>>> sub.email if sub else None
'some_user@talkpython.fm'
```
