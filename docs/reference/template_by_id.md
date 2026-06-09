## template_by_id()


Retrieve a single template by its numeric ID.


Usage

``` python
template_by_id(
    template_id,
    timeout_config=None,
)
```


## Parameters


`template_id: int`  
The numeric ID of the template to retrieve, e.g. 7.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`Optional[models.Template]`  
A models.Template built from the server's response for the given ID.


## Raises


`OperationNotAllowedError`  
If the base URL has not been set or you have not logged in.

`httpx.HTTPStatusError`  
If the server responds with a 4xx or 5xx status (e.g. an unknown template ID).

`ValidationError`  
If the response is empty or is not valid JSON.
