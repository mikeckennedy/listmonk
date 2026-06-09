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


Name and subject are required; all other fields fall back to defaults (for example, `list_ids` defaults to the single list {1} and `from_email` falls back to the instance settings when omitted).


## Parameters


`name: Optional[str] = None`  
The internal name of the campaign. Required.

`subject: Optional[str] = None`  
The email subject line. Required.

`list_ids: Optional[set[int]] = None`  
A set of list IDs to send the campaign to. Defaults to {1}.

`from_email: Optional[str] = None`  
The 'From' address for campaign emails. Defaults to the instance setting when not provided.

`campaign_type: Optional[str] = None`  
The campaign type, 'regular' or 'optin'.

`content_type: Optional[str] = None`  
The body format: 'richtext', 'html', 'markdown', or 'plain'.

`body: Optional[str] = None`  
The campaign body in the configured content type.

`alt_body: Optional[str] = None`  
The optional plain-text alternative body for multipart HTML emails.

`send_at: Optional[datetime.datetime] = None`  
Optional timestamp at which to schedule the campaign.

`messenger: Optional[str] = None`  
The delivery channel, usually 'email'.

`template_id: Optional[int] = None`  
The ID of the template used to render the campaign.

`tags: Optional[list[str]] = None`  
A list of tags to attach to the campaign.

`headers: Optional[dict[str, Optional[str]]] = None`  
A list of custom email headers, each a single-entry dict.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`Optional[models.Campaign]`  
A Campaign object with the full details of the newly created campaign.


## Raises


`ValueError`  
If `name` or `subject` is not provided.

`OperationNotAllowedError`  
If the base URL is not set or you have not logged in.

`httpx.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.

`ValidationError`  
If the server returns an empty body or invalid JSON.


## Examples

``` python
>>> import listmonk
>>> campaign = listmonk.create_campaign(
...     name='June Newsletter',
...     subject='Our June Update',
...     list_ids={1, 2},
...     content_type='html',
...     body='<h1>Hello</h1>',
... )
>>> campaign.id
7
```
