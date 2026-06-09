## models.UpdateCampaignModel


The payload used to update an existing campaign.


Usage

``` python
models.UpdateCampaignModel()
```


Shares all fields with \[CreateCampaignModel\]\[listmonk.models.CreateCampaignModel\]. As a safeguard, a `send_at` value that is already in the past is dropped (set to `None`) before sending, so that updating a campaign does not fail on a stale scheduled time.


## Methods

| Name | Description |
|----|----|
| [serialize_send_at()](#serialize_send_at) | Serialize the provided datetime field to prepare for sending, considering the specified send_at time. |

------------------------------------------------------------------------


#### serialize_send_at()


Serialize the provided datetime field to prepare for sending, considering the specified send_at time.


Usage

``` python
serialize_send_at(fld)
```


If send_at is in the past then the update will fail, so we check if it is in the past and if it is we turn off the campaign scheduled send time.


##### Parameters


`fld: datetime.datetime`  
The datetime field to be serialized.


##### Returns


`Optional[datetime.datetime]`  
The serialized datetime field, or None if the provided field is in the past.
