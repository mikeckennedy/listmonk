## update_template()


Update a template in the system.


Usage

``` python
update_template(
    template,
    timeout_config=None,
)
```


## Parameters


`template: models.Template`  
models.Template - the template object to be updated

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`Optional[models.Template]`  
models.Template - the updated template object after the update operation
