## create_template()


Create a template with the specified details.


Usage

``` python
create_template(
    name=None,
    body=None,
    type=None,
    is_default=None,
    subject=None,
    timeout_config=None
)
```


## Parameters


`name: Optional[str] = None`  
The name of the template.

`body: Optional[str] = None`  
The body content of the template.

`type: Optional[str] = None`  
The type of the template.

`is_default: Optional[bool] = None`  
Indicates if the template is the default one.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`Optional[models.Template]`  
Optional\[models.Template\]: An instance of models.Template representing the created template.
