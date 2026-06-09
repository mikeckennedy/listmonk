## set_default_template()


Set the given template ID as the default template.


Usage

``` python
set_default_template(
    template_id=None,
    timeout_config=None,
)
```


## Parameters


`template_id: Optional[int] = None`  
The ID of the template to set as default. If not provided, a ValueError is raised.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`bool: bool`  
True if the default template was set successfully, False otherwise.
