## models.CreateCampaignModel


The payload used to create a new campaign.


Usage

``` python
models.CreateCampaignModel()
```


This is the raw request body sent to Listmonk; the higher-level [create_campaign](create_campaign.md#listmonk.create_campaign) helper validates that name and subject are present and defaults the target list to `{1}` before populating this model.


## Attributes


`name: Optional[str]`  
The internal campaign name.

`subject: Optional[str]`  
The email subject line.

`lists: list[int]`  
The IDs of the lists to send the campaign to. Defaults to an empty list.

`from_email: Optional[str]`  
The sender (From) address. Omit to use the instance default.

`type: Optional[str]`  
The campaign type, e.g. `regular` or `optin`.

`content_type: Optional[str]`  
The body format, e.g. `richtext`, `html`, `markdown`, or `plain`.

`body: Optional[str]`  
The campaign body in the configured content type.

`altbody: Optional[str]`  
The optional plain-text alternative body for multipart HTML emails.

`send_at: Optional[datetime.datetime]`  
The scheduled send time, if the campaign should be scheduled. Serialized to an ISO-8601 string (or `None`) when sent.

`messenger: Optional[str]`  
The delivery channel, typically `email`.

`template_id: Optional[int]`  
The ID of the template used to render the campaign. Required field that may be `None` (it has no default and must be supplied explicitly).

`tags: list[str]`  
Arbitrary labels to attach to the campaign. Defaults to an empty list.

`headers: list[dict[str, Optional[str]]]`  
Custom email headers to include, each as a single-entry dict. Defaults to an empty list.

`media: list[int]`  
The IDs of uploaded media files to attach to the campaign. Defaults to an empty list.
