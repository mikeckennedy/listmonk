## test_campaign()


Send a one-off test copy of a campaign to specific addresses.


Usage

``` python
test_campaign(
    campaign_id,
    emails,
    timeout_config=None,
)
```


The campaign is left untouched - it stays a draft and its stats are unaffected. Each address must already exist as a subscriber on the instance; Listmonk will not create them, and a test to an unknown address silently delivers nothing.


## Parameters


`campaign_id: int`  
The numeric ID of the campaign to test.

`emails: list[str]`  
The subscriber email addresses to send the test to. Required.

`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`bool`  
True if the server accepted the test send; False if no campaign with the

given ID exists.


## Raises


`ValueError`  
If `campaign_id` is falsy or `emails` is empty.

`OperationNotAllowedError`  
If the base URL is not set or you have not logged in.

`httpx2.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.

`ValidationError`  
If the server returns an empty body or invalid JSON.


## Examples

``` python
>>> import listmonk
>>> listmonk.test_campaign(42, ['you@example.com'])
True
```
