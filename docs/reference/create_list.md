## create_list()


Create a new mailing list on the server.


Usage

``` python
create_list(
    list_name, list_type="public", optin="single", tags=None, description=None
)
```


## Parameters


`list_name: str`  
Name of the new list.

`list_type: str = ``"public"`  
Type of list. Options: "private", "public". Defaults to "public".

`optin: str = ``"single"`  
Opt-in type. Options: "single", "double". Defaults to "single".

`tags: Optional[list[str]] = None`  
Optional list of tags associated with the list.

`description: Optional[str] = None`  
Optional description for the new list.


## Returns


`Optional[models.MailingList]`  
The MailingList object that was created on the server.
