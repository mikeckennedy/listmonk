## delete_campaign()


Completely delete a campaign from your system.


Usage

``` python
delete_campaign(
    campaign_id=None,
    timeout_config=None,
)
```


The campaign is first looked up by ID; if no such campaign exists the function returns False without issuing a delete request.


## Parameters


`campaign_id: Optional[int] = None`  
The numeric ID of the campaign to delete.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`bool`  
True if the campaign was successfully deleted; False if no campaign with

the given ID was found or the server reported it was not deleted.


## Raises


`ValueError`  
If `campaign_id` is not provided.

`OperationNotAllowedError`  
If the base URL is not set or you have not logged in.

`httpx.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.

`ValidationError`  
If the server returns an empty body or invalid JSON.
