## models.CreateTemplateModel


The payload used to create a new template.


Usage

``` python
models.CreateTemplateModel()
```


## Attributes


`name: Optional[str]`  
The template name.

`subject: Optional[str]`  
The default subject line for the template, if any.

`body: Optional[str]`  
The template body markup.

`type: Optional[str]`  
The template type, e.g. `campaign` or `tx` (transactional).

`is_default: Optional[bool]`  
Whether the new template should become the default for its type.
