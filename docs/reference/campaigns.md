## campaigns()


Get campaigns on the server.


Usage

``` python
campaigns(timeout_config=None)
```


## Parameters


`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`list[models.Campaign]`  
List of Campaign objects with the full details of that campaign.
