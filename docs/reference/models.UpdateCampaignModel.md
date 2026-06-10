## models.UpdateCampaignModel


The payload used to update an existing campaign.


Usage

``` python
models.UpdateCampaignModel()
```


Shares all fields with [CreateCampaignModel](models.CreateCampaignModel.md#listmonk.models.CreateCampaignModel). As a safeguard, a `send_at` value that is already in the past is dropped (set to `None`) before sending, so that updating a campaign does not fail on a stale scheduled time.


## Methods

| Name | Description |
|----|----|
| [validate_send_at()](#validate_send_at) | Drop a send_at value that is already in the past. |

------------------------------------------------------------------------


#### validate_send_at()


Drop a send_at value that is already in the past.


Usage

``` python
validate_send_at(fld)
```


Listmonk rejects updates whose scheduled send time has passed, so a past send_at is replaced with None (unscheduling the campaign).


##### Parameters


`fld: datetime.datetime`  
The incoming send_at value.


##### Returns


`Optional[datetime.datetime]`  
The original datetime, or None if it is in the past.
