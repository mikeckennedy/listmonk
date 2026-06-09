## send_transactional_email()


Send a transactional email through Listmonk to the recipient.


Usage

``` python
send_transactional_email(
    subscriber_email,
    template_id,
    from_email=None,
    template_data=None,
    messenger_channel="email",
    content_type="markdown",
    altbody=None,
    attachments=None,
    email_headers=None,
    timeout_config=None
)
```


Errors may show up in the logs section of your Listmonk dashboard.


## Parameters


`subscriber_email: str`  
The email address to send the email to (they must be a subscriber of *some* list on your server).

`template_id: int`  
The template ID to use for the email. It must be a "transactional" not campaign template.

`from_email: Optional[str] = None`  
The from address for the email. Can be omitted to use default email at your output provider.

`template_data: Optional[dict[str, Any]] = None`  
A dictionary of merge parameters for the template, available in the template as {{ .Tx.Data.\* }}.

`messenger_channel: str = ``"email"`  
Default is "email", if you have SMS or some other channel, you can use it here.

`content_type: str = ``"markdown"`  
Email format options include html, markdown, and plain.

`altbody: Optional[str] = None`  
Optional alternate plaintext body for multipart HTML emails.

`attachments: Optional[list[Path]] = None`  
Optional list of `pathlib.Path` objects pointing to file that will be sent as attachment.

`email_headers: Optional[list[dict[str, Optional[str]]]] = None`  
Optional array of e-mail headers to include in all messages sent from this server. eg: \[{"X-Custom": "value"}, {"X-Custom2": "value"}\]

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`bool`  
True if the email send was successful, False otherwise.
