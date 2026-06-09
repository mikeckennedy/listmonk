## subscriber_by_email()


Retrieves the subscribe by email (e.g. "some_user@talkpython.fm")


Usage

``` python
subscriber_by_email(
    email,
    timeout_config=None,
)
```


## Parameters


`email: str`  
Email of the subscriber (e.g. "some_user@talkpython.fm")

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`Optional[models.Subscriber]`  
The subscribe if found, None otherwise.
