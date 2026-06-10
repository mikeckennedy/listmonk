## upload_media()


Upload a file to the Listmonk media library.


Usage

``` python
upload_media(
    file,
    filename=None,
    timeout_config=None,
)
```


The returned Media object's `id` can be passed to [create_campaign()](create_campaign.md#listmonk.create_campaign) or [update_campaign()](update_campaign.md#listmonk.update_campaign) via `media_ids` to attach the file to a campaign.


## Parameters


`file: Path | bytes`  
A Path to a file on disk, or the raw bytes of the file content.

`filename: Optional[str] = None`  
The name to store the file under. Required when `file` is bytes; when `file` is a Path it defaults to the path's file name.

`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`models.Media`  
A Media object describing the uploaded file, including its `id`.


## Raises


`ListmonkFileNotFoundError`  
If `file` is a Path that does not point to an existing file.

`ValueError`  
If `file` is bytes and `filename` is not provided.

`TypeError`  
If `file` is neither a Path nor bytes.

`OperationNotAllowedError`  
If the base URL is not set or you have not logged in.

`httpx2.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.

`ValidationError`  
If the server returns an empty body or invalid JSON.
