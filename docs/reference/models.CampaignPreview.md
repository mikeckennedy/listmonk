## models.CampaignPreview


A rendered preview of a campaign.


Usage

``` python
models.CampaignPreview()
```


## Attributes


`preview: Optional[str]`  
The rendered HTML preview of the campaign body.


## Examples

``` python
>>> import listmonk
>>> preview = listmonk.campaign_preview_by_id(7)
>>> preview.preview[:15]
'<!doctype html>'
```
