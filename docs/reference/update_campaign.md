## update_campaign()


Update an existing campaign with the provided campaign information.


Usage

``` python
update_campaign(
    campaign,
    timeout_config=None,
)
```


The campaign's target lists are normalized to their IDs before sending, and a `send_at` value already in the past is dropped so the update does not fail on a stale scheduled time. After the update succeeds, the campaign is re-fetched from the server and returned.


## Parameters


`campaign: models.Campaign`  
The Campaign object containing the updated information. Must have a valid `id`.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`Optional[models.Campaign]`  
The updated Campaign object as freshly fetched from the server, or None

if the campaign can no longer be found after the update.


## Raises


`ValueError`  
If `campaign` is None or has no `id`.

`OperationNotAllowedError`  
If the base URL is not set or you have not logged in.

`httpx.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.

`ValidationError`  
If the follow-up fetch returns an empty or invalid JSON response.
