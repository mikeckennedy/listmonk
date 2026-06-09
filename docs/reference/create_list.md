## create_list()


Create a new mailing list on the server.


Usage

``` python
create_list(
    list_name, list_type="public", optin="single", tags=None, description=None
)
```


The list name is stripped of surrounding whitespace before submission.


## Parameters


`list_name: str`  
Name of the new list. Required and must be non-empty after whitespace is stripped.

`list_type: str = ``"public"`  
Visibility of the list. One of 'public' or 'private'. Defaults to 'public'.

`optin: str = ``"single"`  
Opt-in mode. One of 'single' or 'double'. Defaults to 'single'.

`tags: Optional[list[str]] = None`  
Optional list of tag strings to associate with the list.

`description: Optional[str] = None`  
Optional free-text description for the new list.


## Returns


`Optional[models.MailingList]`  
The MailingList object that was created on the server, including its

assigned id and uuid.


## Raises


`OperationNotAllowedError`  
If the base URL is not set or you are not logged in.

`ValueError`  
If list_name is empty, or if list_type or optin is not one of its accepted values.

`ValidationError`  
If the server returns an empty or invalid JSON response.

`httpx.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.


## Examples

``` python
>>> import listmonk
>>> new_list = listmonk.create_list('Newsletter', list_type='public', optin='double')
>>> new_list.id
7
```
