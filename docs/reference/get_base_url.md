## get_base_url()


Return the configured base URL of your Listmonk instance.


Usage

``` python
get_base_url()
```


Each Listmonk instance lives at its own address, for example https://listmonk.somedomain.tech. This getter returns whatever value was previously stored by set_url_base().


## Returns


`Optional[str]`  
The base URL of your instance (without a trailing slash), or None if

set_url_base() has not been called yet.
