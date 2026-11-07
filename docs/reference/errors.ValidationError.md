## errors.ValidationError


Raised when an argument fails client-side validation before a request is sent,


Usage

``` python
errors.ValidationError()
```


or when the server returns an empty or malformed JSON response.


## Examples

``` python
>>> import listmonk
>>> from listmonk.errors import ValidationError
>>> try:
...     listmonk.set_url_base('listmonk.somedomain.tech')  # no scheme
... except ValidationError as e:
...     print(e)
The url must start with the HTTP scheme (http:// or https://).
```
