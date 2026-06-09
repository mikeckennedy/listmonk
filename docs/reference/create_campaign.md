## create_campaign()


Create a new campaign with the given parameters.


Usage

``` python
create_campaign(
    name=None,
    subject=None,
    list_ids=None,
    from_email=None,
    campaign_type=None,
    content_type=None,
    body=None,
    alt_body=None,
    send_at=None,
    messenger=None,
    template_id=None,
    tags=None,
    headers=None,
    timeout_config=None
)
```


## Parameters


`name: Optional[str] = None`  
The name of the campaign.

`subject: Optional[str] = None`  
The subject of the campaign.

`list_ids: set[int] = None`  
A set of list IDs to send the campaign to. Defaults to 1.

`from_email: Optional[str] = None`  
'From' email in campaign emails. Defaults to value from settings if not provided.

`campaign_type: Optional[str] = None`  
The type of the campaign: 'regular' or 'optin'.

`content_type: Optional[str] = None`  
The content type of the campaign: 'richtext', 'html', 'markdown', 'plain'.

`body: Optional[str] = None`  
The body of the campaign.

`alt_body: Optional[str] = None`  
The alternative text body of the campaign.

`send_at: Optional[datetime.datetime] = None`  
Timestamp to schedule campaign.

`messenger: Optional[str] = None`  
The messenger for the campaign. Usually 'email'

`template_id: int = None`  
The template ID to be used for the campaign. Defaults to 1.

`tags: list[str] = None`  
A list of tags for the campaign.

`headers: list[dict] = None`  
A list of headers for the campaign.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`CreateCampaignModel: Optional[models.Campaign]`  
A model representing the created campaign.


## Raises


`ValueError`  
If required parameters (name, subject, from_email) are not provided.
