## templates()


This function retrieves a list of all templates available in the system.


Usage

``` python
templates(timeout_config=None)
```


## Parameters


`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`list[models.Template]`  
list of models.Template objects representing the templates available in the system.
