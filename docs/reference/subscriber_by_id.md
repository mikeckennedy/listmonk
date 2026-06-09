## subscriber_by_id()


Retrieves the subscribe by id (e.g. 201)


Usage

``` python
subscriber_by_id(
    subscriber_id,
    timeout_config=None,
)
```


## Parameters


`subscriber_id: int`  
ID of the subscriber (e.g. 201)

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`Optional[models.Subscriber]`  
The subscribe if found, None otherwise.
