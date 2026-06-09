## delete_subscriber()


Completely delete a subscriber from your system (as if they were never there).


Usage

``` python
delete_subscriber(
    email=None, overriding_subscriber_id=None, timeout_config=None
)
```


If your goal is to unsubscribe them rather than erase them, use block_subscriber instead. The email is normalized (lowercased and stripped) before lookup. When both arguments are given, overriding_subscriber_id takes precedence.


## Parameters


`email: Optional[str] = None`  
Email of the subscriber to delete. Required unless overriding_subscriber_id is provided.

`overriding_subscriber_id: Optional[int] = None`  
Optional ID of the subscriber to delete; takes precedence over email.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`bool`  
True if the subscriber was successfully deleted. False if no subscriber matched the given email

(when no overriding id was provided) or if the server reported the delete as unsuccessful.


## Raises


`ValueError`  
If neither email nor overriding_subscriber_id is provided.

`OperationNotAllowedError`  
If the base URL is not set or you are not logged in.

`httpx.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.

`ValidationError`  
If the server returns an empty or invalid JSON response.
