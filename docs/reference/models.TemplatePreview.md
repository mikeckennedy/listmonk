## models.TemplatePreview


A rendered preview of a template.


Usage

``` python
models.TemplatePreview()
```


## Attributes


`preview: Optional[str]`  
The rendered HTML preview of the template, using lorem-ipsum sample content.


## Examples

``` python
>>> import listmonk
>>> preview = listmonk.template_preview_by_id(3)
>>> preview.preview[:15]
'<!doctype html>'
```
