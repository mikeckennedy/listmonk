## models.Campaign


An email campaign on the Listmonk instance.


Usage

``` python
models.Campaign()
```


## Attributes


`id: int`  
The numeric campaign ID assigned by Listmonk.

`created_at: datetime.datetime`  
When the campaign was created.

`updated_at: Optional[datetime.datetime]`  
When the campaign was last modified, if ever.

`views: int`  
The number of times the campaign has been opened/viewed.

`clicks: int`  
The number of link clicks recorded for the campaign.

`lists: list[dict[str, Any]]`  
The target lists for the campaign, each as a dict describing the list.

`started_at: Optional[datetime.datetime]`  
When sending began, if the campaign has started.

`to_send: int`  
The total number of recipients the campaign will be sent to.

`sent: int`  
The number of messages sent so far.

`uuid: str`  
The globally unique identifier for the campaign.

`name: Optional[str]`  
The internal campaign name.

`type: Optional[str]`  
The campaign type, e.g. `regular` or `optin`.

`subject: Optional[str]`  
The email subject line.

`from_email: Optional[str]`  
The sender (From) address.

`body: Optional[str]`  
The campaign body in the configured content type.

`altbody: Optional[str]`  
The optional plain-text alternative body for multipart HTML emails.

`send_at: Optional[datetime.datetime]`  
The scheduled send time, if the campaign is scheduled.

`status: Optional[str]`  
The campaign status, e.g. `draft`, `scheduled`, `running`, `paused`, `cancelled`, or `finished`.

`content_type: Optional[str]`  
The body format, e.g. `richtext`, `html`, `markdown`, or `plain`.

`tags: list[str]`  
Arbitrary labels attached to the campaign.

`template_id: int`  
The ID of the template used to render the campaign.

`messenger: Optional[str]`  
The delivery channel, typically `email`.

`headers: list[dict[str, Optional[str]]]`  
Custom email headers to include, each as a single-entry dict.
