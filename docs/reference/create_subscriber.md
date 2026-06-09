## create_subscriber()


Create a new subscriber on the Listmonk server.


Usage

``` python
create_subscriber(
    email,
    name=None,
    list_ids=None,
    pre_confirm=False,
    attribs=None,
    timeout_config=None
)
```


## Parameters


`email: str`  
Email of the subscriber.

`name: Optional[str] = None`  
Full name (first\[SPACE\]last) of the subscriber

`list_ids: set[int] = None`  
List of list IDs for the lists to add them to (say that 3 times fast!)

`pre_confirm: bool = ``False`  
Whether to preconfirm the subscriber for double opt-in lists (no email to them)

`attribs: Optional[dict[str, Any]] = None`  
Custom dictionary for the attribs data on the user record (queryable in the subscriber UI).

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`models.Subscriber`  
The Subscribe object that was created on the server with ID, UUID, and much more.
