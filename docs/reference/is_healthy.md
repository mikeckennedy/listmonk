## is_healthy()


Check whether the server is reachable and the stored credentials are valid.


Usage

``` python
is_healthy(timeout_config=None)
```


Issues an authenticated GET to the Listmonk health endpoint using the cached username and password. This call is defensive: any failure--the URL base not being set, not being logged in, a network error, a non-2xx response, or an unparseable body--is caught and reported as False, so it never raises.


## Parameters


`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`bool`  
True if the server responded healthy with valid credentials, False

otherwise.
