## create_template()


Create a new template on the Listmonk instance.


Usage

``` python
create_template(
    name, body, type=None, is_default=None, subject=None, timeout_config=None
)
```


The body must contain the placeholder {{ template "content" . }} exactly where the rendered content should be injected; a template is rejected without it.


## Parameters


`name: str`  
The template name. Required; a ValueError is raised if empty.

`body: str`  
The template body markup. Required, and must contain the {{ template "content" . }} placeholder.

`type: Optional[str] = None`  
The template type, e.g. 'campaign' or 'tx' (transactional).

`is_default: Optional[bool] = None`  
Whether the new template should become the default for its type.

`subject: Optional[str] = None`  
The default subject line for the template, if any.

`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`models.Template`  
A models.Template representing the newly created template.


## Raises


`ValueError`  
If name is empty, if body is empty, or if body does not contain the {{ template "content" . }} placeholder.

`OperationNotAllowedError`  
If the base URL has not been set or you have not logged in.

`httpx2.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.

`ValidationError`  
If the response is empty or is not valid JSON.


## Examples

``` python
>>> import listmonk
>>> body = 'Header {{ template "content" . }} Footer'
>>> tmpl = listmonk.create_template(name='Welcome', body=body, type='tx')
>>> tmpl.id
7
```
