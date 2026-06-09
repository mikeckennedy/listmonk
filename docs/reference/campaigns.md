## campaigns()


Get all campaigns on the server.


Usage

``` python
campaigns(timeout_config=None)
```


Fetches the full list of campaigns in a single request (the server is asked for up to one million results per page), so no pagination is required.


## Parameters


`timeout_config: Optional[httpx.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`list[models.Campaign]`  
A list of Campaign objects, each with the full details of that campaign.

Returns an empty list if the instance has no campaigns.


## Raises


`OperationNotAllowedError`  
If the base URL is not set or you have not logged in.

`httpx.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.

`ValidationError`  
If the server returns an empty body or invalid JSON.
