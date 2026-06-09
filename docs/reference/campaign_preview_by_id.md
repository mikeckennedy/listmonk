## campaign_preview_by_id()


Get the rendered preview of a campaign with the given ID.


Usage

``` python
campaign_preview_by_id(
    campaign_id,
    timeout_config=None,
)
```


## Parameters


`campaign_id: int`  
The numeric ID of the campaign to preview, e.g. 7.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`Optional[models.CampaignPreview]`  
A CampaignPreview object whose `preview` attribute holds the rendered

HTML body returned by the server.


## Raises


`OperationNotAllowedError`  
If the base URL is not set or you have not logged in.

`httpx.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.
