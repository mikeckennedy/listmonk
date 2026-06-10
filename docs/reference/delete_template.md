## delete_template()


Permanently delete a template from the Listmonk instance.


Usage

``` python
delete_template(
    template_id,
    timeout_config=None,
)
```


The template is first looked up by ID; if it does not exist, no delete is attempted and False is returned.


## Parameters


`template_id: int`  
The numeric ID of the template to delete. Required.

`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`bool`  
True if the template was deleted successfully. False if no template with

the given ID exists.


## Raises


`ValueError`  
If template_id is falsy (e.g. 0).

`OperationNotAllowedError`  
If the base URL has not been set or you have not logged in.

`httpx2.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.

`ValidationError`  
If the response is empty or is not valid JSON.
