## subscriber_by_uuid()


Retrieves the subscriber by uuid (e.g. "c37786af-e6ab-4260-9b49-740adpcm6ed")


Usage

``` python
subscriber_by_uuid(
    subscriber_uuid,
    timeout_config=None,
)
```


## Parameters


`subscriber_uuid: str`  
UUID of the subscriber (e.g. "c37786af-e6ab-4260-9b49-740aaaa6ed")

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`Optional[models.Subscriber]`  
The subscribe if found, None otherwise.
