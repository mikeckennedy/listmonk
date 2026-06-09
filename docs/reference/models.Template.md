## models.Template


An email template on the Listmonk instance.


Usage

``` python
models.Template()
```


## Attributes


`id: int`  
The numeric template ID assigned by Listmonk.

`created_at: datetime.datetime`  
When the template was created.

`updated_at: Optional[datetime.datetime]`  
When the template was last modified, if ever.

`name: Optional[str]`  
The template name.

`subject: Optional[str]`  
The default subject line for the template, if any.

`body: Optional[str]`  
The template body markup.

`type: Optional[str]`  
The template type, e.g. `campaign` or `tx` (transactional).

`is_default: Optional[bool]`  
Whether this is the default template for its type.
