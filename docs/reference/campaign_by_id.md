## campaign_by_id()


Get the full details of a campaign with the given ID.


Usage

``` python
campaign_by_id(
    campaign_id,
    timeout_config=None,
)
```


## Parameters


`campaign_id: int`  
The numeric ID of the campaign to fetch, e.g. 7.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`Optional[models.Campaign]`  
A Campaign object with the full details of the campaign, or None if the

server returns no campaign data for the given ID.


## Raises


`OperationNotAllowedError`  
If the base URL is not set or you have not logged in.

`httpx.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.

`ValidationError`  
If the server returns an empty body or invalid JSON.
