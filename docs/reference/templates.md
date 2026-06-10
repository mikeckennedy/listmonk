## templates()


Retrieve all templates defined on the Listmonk instance.


Usage

``` python
templates(timeout_config=None)
```


This fetches both campaign and transactional templates in a single (large) paginated request.


## Parameters


`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`list[models.Template]`  
A list of models.Template objects, one per template on the server.

Returns an empty list if no templates are defined.


## Raises


`OperationNotAllowedError`  
If the base URL has not been set or you have not logged in.

`httpx2.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.

`ValidationError`  
If the response is empty or is not valid JSON.
