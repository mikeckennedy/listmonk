## pause_campaign()


Pause a campaign that is currently sending.


Usage

``` python
pause_campaign(
    campaign_id,
    timeout_config=None,
)
```


This is a convenience wrapper around set_campaign_status that sets the status to CampaignStatuses.paused. A paused campaign can be resumed with start_campaign().


## Parameters


`campaign_id: int`  
The numeric ID of the campaign to pause.

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
If the server rejects the transition (for example pausing a campaign that is not running).

`ValidationError`  
If the server returns an empty body or invalid JSON.


## Examples

``` python
>>> import listmonk
>>> listmonk.pause_campaign(42)
```
