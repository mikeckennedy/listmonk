## block_subscriber()


Add a subscriber to the blocklist, AKA unsubscribe them.


Usage

``` python
block_subscriber(
    subscriber,
    timeout_config=None,
)
```


## Parameters


`subscriber: models.Subscriber`  
The subscriber to block/unsubscribe.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`Optional[models.Subscriber]`  
The updated subscriber object from the server.
