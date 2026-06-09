## enable_subscriber()


Set a subscriber's status to enable.


Usage

``` python
enable_subscriber(
    subscriber,
    timeout_config=None,
)
```


## Parameters


`subscriber: models.Subscriber`  
The subscriber to enable.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`Optional[models.Subscriber]`  
The updated subscriber object from the server.
