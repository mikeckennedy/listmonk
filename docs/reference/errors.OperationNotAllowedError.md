## errors.OperationNotAllowedError


Raised when an operation is not permitted in the client's current state.


Usage

``` python
errors.OperationNotAllowedError()
```


For example, calling an API before the base URL has been set, or before a successful login. It subclasses ValidationError, so an `except ValidationError` clause catches it too.


## Examples

``` python
>>> import listmonk
>>> from listmonk.errors import OperationNotAllowedError
>>> try:
...     listmonk.lists()  # before set_url_base() and login()
... except OperationNotAllowedError as e:
...     print(e)
URL Base must be set to proceed.
```
