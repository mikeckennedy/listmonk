## delete_campaign()


Completely delete a campaign from your system.


Usage

``` python
delete_campaign(
    campaign_id=None,
    timeout_config=None,
)
```


## Parameters


`campaign_id: Optional[int] = None`  
name of the campaign to delete.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`bool`  
True if the campaign was successfully deleted, False otherwise.
