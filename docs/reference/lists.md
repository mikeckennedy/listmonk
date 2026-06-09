## lists()


Get mailing lists on the server.


Usage

``` python
lists(timeout_config=None)
```


## Parameters


`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`list[models.MailingList]`  
List of MailingList objects with the full details of that list.
