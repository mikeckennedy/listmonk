## disable_subscriber()


Set a subscriber's status to disable.


Usage

``` python
disable_subscriber(
    subscriber,
    timeout_config=None,
)
```


## Parameters


`subscriber: Optional[models.Subscriber]`  
The subscriber to disable.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`Optional[models.Subscriber]`  
The updated subscriber object from the server.
