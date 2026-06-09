## verify_login()


Call to verify that the stored auth token is still valid.


Usage

``` python
verify_login(timeout_config=None)
```


## Parameters


`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`bool`  
True if the stored auth token is still value, False otherwise.
