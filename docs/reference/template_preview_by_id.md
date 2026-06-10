## template_preview_by_id()


Render and return a preview of a template.


Usage

``` python
template_preview_by_id(
    template_id,
    timeout_config=None,
)
```


The preview is rendered by the server using lorem-ipsum sample content, so it can be inspected without sending real data through the template.


## Parameters


`template_id: int`  
The numeric ID of the template to preview, e.g. 7.

`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`models.TemplatePreview`  
A models.TemplatePreview whose 'preview' field holds the rendered HTML.


## Raises


`OperationNotAllowedError`  
If the base URL has not been set or you have not logged in.

`httpx2.HTTPStatusError`  
If the server responds with a 4xx or 5xx status (e.g. an unknown template ID).
