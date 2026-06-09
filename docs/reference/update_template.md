## update_template()


Update an existing template on the Listmonk instance.


Usage

``` python
update_template(
    template,
    timeout_config=None,
)
```


The template's name, subject, body, and type are sent in the update; the is_default flag is not changed by this call (use set_default_template for that). After the update succeeds, the template is re-fetched and returned.


## Parameters


`template: models.Template`  
The models.Template to update. Must be non-None and have an id.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`Optional[models.Template]`  
A freshly fetched models.Template reflecting the saved changes.


## Raises


`ValueError`  
If template is None or has no id.

`OperationNotAllowedError`  
If the base URL has not been set or you have not logged in.

`httpx.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.

`ValidationError`  
If the re-fetch response is empty or is not valid JSON.
