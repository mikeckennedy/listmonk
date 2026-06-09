## campaign_preview_by_id()


Get the preview of a campaign with the given ID.


Usage

``` python
campaign_preview_by_id(
    campaign_id,
    timeout_config=None,
)
```


## Parameters


`campaign_id: int`  
A campaign to get the details about, e.g. 7.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`Optional[models.CampaignPreview]`  
String preview of the campaign.
