## lists()


Get all mailing lists on the server.


Usage

``` python
lists(timeout_config=None)
```


Retrieves every mailing list in a single request (paged at one large page), so no manual pagination is required.


## Parameters


`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`list[models.MailingList]`  
A list of MailingList objects with the full details of each list. Returns

an empty list if the server has no mailing lists.


## Raises


`OperationNotAllowedError`  
If the base URL is not set or you are not logged in.

`ValidationError`  
If the server returns an empty or invalid JSON response.

`httpx2.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.
