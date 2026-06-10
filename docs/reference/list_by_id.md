## list_by_id()


Get the full details of a single mailing list by its ID.


Usage

``` python
list_by_id(
    list_id,
    timeout_config=None,
)
```


## Parameters


`list_id: int`  
The numeric ID of the list to retrieve, e.g. 7.

`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`models.MailingList`  
A MailingList object with the full details of the requested list.


## Raises


`OperationNotAllowedError`  
If the base URL is not set or you are not logged in.

`ValidationError`  
If the server returns an empty or invalid JSON response.

`httpx2.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.

`Exception`  
If the server returns a result set that does not contain the requested list_id (a workaround for a known Listmonk server quirk).
