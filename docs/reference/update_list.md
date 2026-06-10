## update_list()


Update an existing mailing list on the server.


Usage

``` python
update_list(
    list_id,
    list_name=None,
    list_type=None,
    status=None,
    optin=None,
    tags=None,
    description=None,
    timeout_config=None
)
```


Only the parameters you pass (that are not None) are included in the update payload, so omitted fields are left unchanged.


## Parameters


`list_id: int`  
The numeric ID of the list to update. Required.

`list_name: Optional[str] = None`  
Optional new name for the list (stripped of surrounding whitespace).

`list_type: Optional[str] = None`  
Optional new visibility. One of 'public' or 'private'.

`status: Optional[str] = None`  
Optional new status. One of 'active' or 'archived'.

`optin: Optional[str] = None`  
Optional new opt-in mode. One of 'single' or 'double'.

`tags: Optional[list[str]] = None`  
Optional new list of tag strings for the list.

`description: Optional[str] = None`  
Optional new description for the list.

`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`models.MailingList`  
The updated MailingList object as returned by the server.


## Raises


`OperationNotAllowedError`  
If the base URL is not set or you are not logged in.

`ValueError`  
If list_id is missing, or if list_type, status, or optin is not one of its accepted values.

`ValidationError`  
If the server returns an empty or invalid JSON response.

`httpx2.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.
