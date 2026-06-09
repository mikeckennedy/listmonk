## template_preview_by_id()


Get the preview of a template with the given ID.


Usage

``` python
template_preview_by_id(
    template_id,
    timeout_config=None,
)
```


## Parameters


`template_id: int`  
A campaign to get the details about, e.g. 7.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`Optional[models.TemplatePreview]`  
String preview of the template with lorem ipsum.
