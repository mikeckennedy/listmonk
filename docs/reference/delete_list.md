## delete_list()


Delete a mailing list by its ID.


Usage

``` python
delete_list(
    list_id,
    timeout_config=None,
)
```


The list's existence is checked first via list_by_id, which raises if the list does not exist.


## Parameters


`list_id: int`  
The numeric ID of the list to delete. Must be a truthy value (0 or None is rejected).

`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`bool`  
True if the server reports the list was deleted, False if the server

response does not confirm deletion.


## Raises


`OperationNotAllowedError`  
If the base URL is not set or you are not logged in.

`ValueError`  
If list_id is missing or falsy.

`ValidationError`  
If the server returns an empty or invalid JSON response.

`httpx2.HTTPStatusError`  
If the server responds with a 4xx or 5xx status, including when the existence check finds no list with the given ID.
