## list_by_id()


Get the full details of a list with the given ID.


Usage

``` python
list_by_id(
    list_id,
    timeout_config=None,
)
```


## Parameters


`list_id: int`  
A list to get the details about, e.g. 7.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`Optional[models.MailingList]`  
MailingList object with the full details of a list.
