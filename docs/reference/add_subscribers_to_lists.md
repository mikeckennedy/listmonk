## add_subscribers_to_lists()


Add a number of subscribers to a number of lists in a single bulk operation.


Usage

``` python
add_subscribers_to_lists(
    subscriber_ids, list_ids, timeout_config=None, status="confirmed"
)
```


## Parameters


`subscriber_ids: typing.Iterable[int]`  
An iterable of subscriber IDs to add. Duplicates are de-duplicated.

`list_ids: typing.Iterable[int]`  
An iterable of target list IDs to subscribe them to. Duplicates are de-duplicated.

`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.

`status: str = ``"confirmed"`  
The subscription status to assign on the target lists, e.g. 'confirmed' or 'unconfirmed'. Defaults to 'confirmed'.


## Returns


`bool`  
True on success. False if either ID set is empty or contains only 0, or if the server responds with an

error status.


## Raises


`OperationNotAllowedError`  
If the base URL is not set or you are not logged in.
