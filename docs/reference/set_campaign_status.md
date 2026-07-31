## set_campaign_status()


Move a campaign to a new lifecycle status.


Usage

``` python
set_campaign_status(
    campaign_id,
    status,
    timeout_config=None,
)
```


This is how a campaign is actually sent: a draft only begins delivering once its status becomes [running](models.CampaignStatuses.md#listmonk.models.CampaignStatuses.running). Setting [paused](models.CampaignStatuses.md#listmonk.models.CampaignStatuses.paused) halts an in-flight send and [cancelled](models.CampaignStatuses.md#listmonk.models.CampaignStatuses.cancelled) stops it for good. Note that [update_campaign()](update_campaign.md#listmonk.update_campaign) cannot do this; the server exposes status changes on a separate endpoint.


## Parameters


`campaign_id: int`  
The numeric ID of the campaign to transition.

`status: models.CampaignStatuses`  
The new status. Use the CampaignStatuses enum.

`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`Optional[models.Campaign]`  
The updated Campaign as returned by the server, or None if no campaign with

the given ID exists.


## Raises


`ValueError`  
If `campaign_id` is falsy (e.g. 0).

`OperationNotAllowedError`  
If the base URL is not set or you have not logged in.

`httpx2.HTTPStatusError`  
If the server rejects the transition (for example starting a campaign that has already finished).

`ValidationError`  
If the server returns an empty body or invalid JSON.


## Examples

``` python
>>> import listmonk
>>> from listmonk.models import CampaignStatuses
>>> listmonk.set_campaign_status(42, CampaignStatuses.running)
```
