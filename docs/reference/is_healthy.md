## is_healthy()


Checks that the token retrieved during login is still valid at your server.


Usage

``` python
is_healthy(timeout_config=None)
```


## Parameters


`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`bool`  
True if the token is still valid, False otherwise.
