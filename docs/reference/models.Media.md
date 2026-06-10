## models.Media


A file uploaded to the Listmonk media library.


Usage

``` python
models.Media()
```


## Attributes


`id: int`  
The numeric media ID assigned by Listmonk. Pass it to [create_campaign](create_campaign.md#listmonk.create_campaign) or [update_campaign](update_campaign.md#listmonk.update_campaign) via `media_ids` to attach the file to a campaign.

`uuid: str`  
The globally unique identifier for the media file.

`filename: Optional[str]`  
The name the file was stored under.

`content_type: Optional[str]`  
The MIME type of the file, if reported by the server.

`created_at: Optional[datetime.datetime]`  
When the file was uploaded.

`uri: Optional[str]`  
The server path the uploaded file is served from.

`thumb_uri: Optional[str]`  
The server path of the generated thumbnail, if any.
