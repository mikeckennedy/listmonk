## delete_list()


Delete a mailing list by its ID.


Usage

``` python
delete_list(list_id)
```


The list's existence is checked first via list_by_id; if it does not exist, no delete request is sent and False is returned.


## Parameters


`list_id: int`  
The numeric ID of the list to delete. Must be a truthy value (0 or None is rejected).


## Returns


`bool`  
True if the server reports the list was deleted, False if the list does

not exist or the server response does not confirm deletion.


## Raises


`OperationNotAllowedError`  
If the base URL is not set or you are not logged in.

`ValueError`  
If list_id is missing or falsy.

`ValidationError`  
If the server returns an empty or invalid JSON response.

`httpx.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.
