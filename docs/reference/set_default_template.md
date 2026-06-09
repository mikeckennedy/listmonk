## set_default_template()


Mark the given template as the default for its type.


Usage

``` python
set_default_template(
    template_id=None,
    timeout_config=None,
)
```


The template is first looked up by ID; if it does not exist, the default is not changed and False is returned.


## Parameters


`template_id: Optional[int] = None`  
The numeric ID of the template to set as default. Required.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`bool`  
True if the default was set successfully. False if no template with the

given ID exists.


## Raises


`ValueError`  
If template_id is missing or falsy.

`OperationNotAllowedError`  
If the base URL has not been set or you have not logged in.

`httpx.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.

`ValidationError`  
If the response is empty or is not valid JSON.
