## subscribers()


Get the list of subscribers matching the given criteria, or all subscribers if no criteria are given.


Usage

``` python
subscribers(
    query_text=None,
    list_id=None,
    timeout_config=None,
)
```


Results are fetched page by page (500 per page) and combined, so a broad query may issue several HTTP requests and return a large list. Subscribers are ordered by `updated_at` descending.


## Parameters


`query_text: Optional[str] = None`  
Optional SQL-like filter applied server-side, e.g. `"subscribers.attribs->>'city' = 'Portland'"`. See https://listmonk.app/docs/querying-and-segmentation/ for the syntax. Defaults to None (no filter).

`list_id: Optional[int] = None`  
Optional list ID; when given, only subscribers belonging to that list (and matching `query_text`, if any) are returned. Defaults to None.

`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`list[models.Subscriber]`  
A list of models.Subscriber objects matching the criteria. Returns an empty list

(never None) if nothing matches.


## Raises


`OperationNotAllowedError`  
If the base URL has not been set or you have not logged in.

`ValidationError`  
If the server returns an empty body or invalid JSON.

`httpx2.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.
