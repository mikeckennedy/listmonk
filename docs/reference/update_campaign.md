## update_campaign()


Update the given campaign with the provided campaign information.


Usage

``` python
update_campaign(
    campaign,
    timeout_config=None,
)
```


## Parameters


`campaign: models.Campaign`  
models.Campaign - The campaign object containing the updated information.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`Optional[models.Campaign]`  
models.Campaign - The updated campaign object from api.


## Raises


`ValueError`  
If the campaign parameter is None or if the campaign id is not present.
