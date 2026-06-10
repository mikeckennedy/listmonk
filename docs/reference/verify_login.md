## verify_login()


Verify that the stored login credentials are still valid at the server.


Usage

``` python
verify_login(timeout_config=None)
```


This is a thin alias for is_healthy(): it issues an authenticated request to the server's health endpoint using the cached credentials. Any error (not logged in, network failure, rejected credentials) is reported as False rather than raised.


## Parameters


`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`bool`  
True if the stored credentials are still valid, False otherwise.
