## delete_subscriber()


Completely delete a subscriber from your system (it's as if they were never there).


Usage

``` python
delete_subscriber(
    email=None, overriding_subscriber_id=None, timeout_config=None
)
```


If your goal is to unsubscribe them, then use the block_subscriber method.


## Parameters


`email: Optional[str] = None`  
Email of the account to delete.

`overriding_subscriber_id: Optional[int] = None`  
Optional ID of the account to delete (takes precedence).

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`bool`  
True if they were successfully deleted, False otherwise.
