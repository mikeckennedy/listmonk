## start_campaign()


Start sending a campaign.


Usage

``` python
start_campaign(
    campaign_id,
    timeout_config=None,
)
```


This is a convenience wrapper around set_campaign_status that sets the status to CampaignStatuses.running.


## Parameters


`campaign_id: int`  
The numeric ID of the campaign to start.

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
>>> listmonk.start_campaign(42)
```
