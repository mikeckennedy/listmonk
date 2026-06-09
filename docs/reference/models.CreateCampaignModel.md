## models.CreateCampaignModel


The payload used to create a new campaign.


Usage

``` python
models.CreateCampaignModel()
```


## Attributes


`name: Optional[str]`  
The internal campaign name.

`subject: Optional[str]`  
The email subject line.

`lists: list[int]`  
The IDs of the lists to send the campaign to.

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
The scheduled send time, if the campaign should be scheduled.

`messenger: Optional[str]`  
The delivery channel, typically `email`.

`template_id: Optional[int]`  
The ID of the template used to render the campaign.

`tags: list[str]`  
Arbitrary labels to attach to the campaign.

`headers: list[dict[str, Optional[str]]]`  
Custom email headers to include, each as a single-entry dict.
