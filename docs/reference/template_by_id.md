## template_by_id()


Retrieve a template by its ID.


Usage

``` python
template_by_id(
    template_id,
    timeout_config=None,
)
```


## Parameters


`template_id: int`  
The ID of the template to retrieve.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`Optional[models.Template]`  
Optional\[models.Template\]: The template object retrieved based on the ID provided.
