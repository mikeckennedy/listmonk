## errors.ListmonkFileNotFoundError


Raised when a local file referenced for upload (e.g. a transactional email attachment) cannot be found.


Usage

``` python
errors.ListmonkFileNotFoundError()
```


## Examples

``` python
>>> import listmonk
>>> from pathlib import Path
>>> from listmonk.errors import ListmonkFileNotFoundError
>>> try:
...     listmonk.upload_media(Path('/no/such/chart.png'))
... except ListmonkFileNotFoundError as e:
...     print(e)
File /no/such/chart.png does not exist
```
