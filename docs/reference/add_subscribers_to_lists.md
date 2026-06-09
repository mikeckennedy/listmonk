## add_subscribers_to_lists()


Add a number of subscribers to a number of lists.


Usage

``` python
add_subscribers_to_lists(
    subscriber_ids, list_ids, timeout_config=None, status="confirmed"
)
```


## Parameters


`subscriber_ids: typing.Iterable[int]`  
List of subscriber IDs.

`list_ids: typing.Iterable[int]`  
List of lists to subscribe to.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`bool`  
True on success, False on fail.
