## delete_template()


Completely delete a template from your system.


Usage

``` python
delete_template(
    template_id=None,
    timeout_config=None,
)
```


## Parameters


`template_id: Optional[int] = None`  
name of the template to delete.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`bool`  
True if the template was successfully deleted, False otherwise.
