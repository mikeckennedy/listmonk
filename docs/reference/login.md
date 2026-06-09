## login()


Log into Listmonk and cache the credentials for the life of your app.


Usage

``` python
login(
    user_name,
    pw,
    timeout_config=None,
)
```


The username and password are validated against the server's health endpoint using HTTP Basic auth. On success they are stored in module-level state and reused by every subsequent API call, so you only need to call this once. set_url_base() must be called first.


## Parameters


`user_name: str`  
Your Listmonk username.

`pw: str`  
Your Listmonk password.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`bool`  
True if the credentials were accepted by the server. Returns False if

the server rejected them or could not be reached (no HTTP error is

raised in that case).


## Raises


`OperationNotAllowedError`  
If the base URL has not been set via set_url_base().

`ValidationError`  
If user_name or pw is empty.


## Examples

``` python
>>> import listmonk
>>> listmonk.set_url_base('https://listmonk.somedomain.tech')
>>> listmonk.login('admin', 'super-secret')
True
```
