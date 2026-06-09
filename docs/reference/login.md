## login()


Logs into Listmonk and stores that authentication for the life of your app.


Usage

``` python
login(
    user_name,
    pw,
    timeout_config=None,
)
```


## Parameters


`user_name: str`  
Your Listmonk username

`pw: str`  
Your Listmonk password

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`bool`  
Returns a boolean indicating whether the login was successful.
