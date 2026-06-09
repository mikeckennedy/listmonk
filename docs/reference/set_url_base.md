## set_url_base()


Set the base URL of your Listmonk instance for all subsequent calls.


Usage

``` python
set_url_base(url)
```


Each Listmonk instance lives at its own address, for example https://listmonk.somedomain.tech. This must be called before login() and any other API operation. A trailing slash, if present, is removed.


## Parameters


`url: str`  
The base URL of your instance, including the http:// or https:// scheme but without the /api path segment.


## Raises


`ValidationError`  
If url is empty or whitespace, or if it does not start with the http:// or https:// scheme.
