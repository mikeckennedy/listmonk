## update_list()


Updates an existing mailing list on the server.


Usage

``` python
update_list(
    list_id,
    list_name=None,
    list_type=None,
    status=None,
    optin=None,
    tags=None,
    description=None
)
```


## Parameters


`list_id: int`  
List ID

`list_name: Optional[str] = None`  
Optional update name of the list.

`list_type: Optional[str] = None`  
Optional update type of list. Options: "private", "public".

`optin: Optional[str] = None`  
Optianal update opt-in type. Options: "single", "double".

`tags: Optional[list[str]] = None`  
Optional update list of tags associated with the list.

`description: Optional[str] = None`  
Optional update description for the list.


## Returns


`Optional[models.MailingList]`  
The MailingList object that was created on the server.
