# API Reference


The full listmonk client API: configuration, list/subscriber/campaign/template management, and transactional email.


## Configuration & Authentication


Point the client at your Listmonk instance and authenticate.


[set_url_base()](set_url_base.md#listmonk.set_url_base)  
Set the base URL of your Listmonk instance for all subsequent calls.

[get_base_url()](get_base_url.md#listmonk.get_base_url)  
Return the configured base URL of your Listmonk instance.

[login()](login.md#listmonk.login)  
Log into Listmonk and cache the credentials for the life of your app.

[verify_login()](verify_login.md#listmonk.verify_login)  
Verify that the stored login credentials are still valid at the server.

[is_healthy()](is_healthy.md#listmonk.is_healthy)  
Check whether the server is reachable and the stored credentials are valid.


## Mailing Lists


Read and manage mailing lists.


[lists()](lists.md#listmonk.lists)  
Get all mailing lists on the server.

[list_by_id()](list_by_id.md#listmonk.list_by_id)  
Get the full details of a single mailing list by its ID.

[create_list()](create_list.md#listmonk.create_list)  
Create a new mailing list on the server.

[update_list()](update_list.md#listmonk.update_list)  
Update an existing mailing list on the server.

[delete_list()](delete_list.md#listmonk.delete_list)  
Delete a mailing list by its ID.


## Subscribers


Create, query, update, and manage the status of subscribers.


[subscribers()](subscribers.md#listmonk.subscribers)  
Get the list of subscribers matching the given criteria, or all subscribers if no criteria are given.

[subscriber_by_email()](subscriber_by_email.md#listmonk.subscriber_by_email)  
Retrieve a single subscriber by their email address (e.g. "some_user@talkpython.fm").

[subscriber_by_id()](subscriber_by_id.md#listmonk.subscriber_by_id)  
Retrieve a single subscriber by their numeric Listmonk ID (e.g. 201).

[subscriber_by_uuid()](subscriber_by_uuid.md#listmonk.subscriber_by_uuid)  
Retrieve a single subscriber by their UUID (e.g. "c37786af-e6ab-4260-9b49-740adpcm6ed").

[create_subscriber()](create_subscriber.md#listmonk.create_subscriber)  
Create a new subscriber on the Listmonk server.

[update_subscriber()](update_subscriber.md#listmonk.update_subscriber)  
Update many aspects of a subscriber: email and name, custom attribute data, list membership, and status.

[add_subscribers_to_lists()](add_subscribers_to_lists.md#listmonk.add_subscribers_to_lists)  
Add a number of subscribers to a number of lists in a single bulk operation.

[enable_subscriber()](enable_subscriber.md#listmonk.enable_subscriber)  
Set a subscriber's status to enabled so they will receive campaigns.

[disable_subscriber()](disable_subscriber.md#listmonk.disable_subscriber)  
Set a subscriber's status to disabled, pausing their subscription so they will not receive campaigns.

[block_subscriber()](block_subscriber.md#listmonk.block_subscriber)  
Add a subscriber to the blocklist, effectively unsubscribing them so they will not receive any mail.

[confirm_optin()](confirm_optin.md#listmonk.confirm_optin)  
Confirm a subscriber's opt-in to a list via the API.

[delete_subscriber()](delete_subscriber.md#listmonk.delete_subscriber)  
Completely delete a subscriber from your system (as if they were never there).


## Campaigns


Create, preview, update, and delete email campaigns.


[campaigns()](campaigns.md#listmonk.campaigns)  
Get all campaigns on the server.

[campaign_by_id()](campaign_by_id.md#listmonk.campaign_by_id)  
Get the full details of a campaign with the given ID.

[campaign_preview_by_id()](campaign_preview_by_id.md#listmonk.campaign_preview_by_id)  
Get the rendered preview of a campaign with the given ID.

[create_campaign()](create_campaign.md#listmonk.create_campaign)  
Create a new campaign with the given parameters.

[update_campaign()](update_campaign.md#listmonk.update_campaign)  
Update an existing campaign with the provided campaign information.

[delete_campaign()](delete_campaign.md#listmonk.delete_campaign)  
Completely delete a campaign from your system.


## Templates


Manage email templates and set the default.


[templates()](templates.md#listmonk.templates)  
Retrieve all templates defined on the Listmonk instance.

[template_by_id()](template_by_id.md#listmonk.template_by_id)  
Retrieve a single template by its numeric ID.

[template_preview_by_id()](template_preview_by_id.md#listmonk.template_preview_by_id)  
Render and return a preview of a template.

[create_template()](create_template.md#listmonk.create_template)  
Create a new template on the Listmonk instance.

[update_template()](update_template.md#listmonk.update_template)  
Update an existing template on the Listmonk instance.

[set_default_template()](set_default_template.md#listmonk.set_default_template)  
Mark the given template as the default for its type.

[delete_template()](delete_template.md#listmonk.delete_template)  
Permanently delete a template from the Listmonk instance.


## Transactional Email


Send one-off transactional messages.


[send_transactional_email()](send_transactional_email.md#listmonk.send_transactional_email)  
Send a transactional email through Listmonk to a single recipient.


## Data Models


Pydantic models returned by and passed to the API functions.


[models.MailingList](models.MailingList.md#listmonk.models.MailingList)  
A mailing list on the Listmonk instance.

[models.SubscriberStatus](models.SubscriberStatus.md#listmonk.models.SubscriberStatus)  
A breakdown of subscriber counts by subscription status for a mailing list.

[models.SubscriberStatuses](models.SubscriberStatuses.md#listmonk.models.SubscriberStatuses)  
The subscription status of a subscriber within a given mailing list.

[models.Subscriber](models.Subscriber.md#listmonk.models.Subscriber)  
A subscriber (contact) on the Listmonk instance.

[models.CreateSubscriberModel](models.CreateSubscriberModel.md#listmonk.models.CreateSubscriberModel)  
The payload used to create a new subscriber.

[models.Campaign](models.Campaign.md#listmonk.models.Campaign)  
An email campaign on the Listmonk instance.

[models.CreateCampaignModel](models.CreateCampaignModel.md#listmonk.models.CreateCampaignModel)  
The payload used to create a new campaign.

[models.UpdateCampaignModel](models.UpdateCampaignModel.md#listmonk.models.UpdateCampaignModel)  
The payload used to update an existing campaign.

[models.CampaignPreview](models.CampaignPreview.md#listmonk.models.CampaignPreview)  
A rendered preview of a campaign.

[models.Template](models.Template.md#listmonk.models.Template)  
An email template on the Listmonk instance.

[models.CreateTemplateModel](models.CreateTemplateModel.md#listmonk.models.CreateTemplateModel)  
The payload used to create a new template.

[models.TemplatePreview](models.TemplatePreview.md#listmonk.models.TemplatePreview)  
A rendered preview of a template.


## Exceptions


Errors raised by the client.


[errors.ValidationError](errors.ValidationError.md#listmonk.errors.ValidationError)  
Raised when an argument fails client-side validation before a request is sent.

[errors.OperationNotAllowedError](errors.OperationNotAllowedError.md#listmonk.errors.OperationNotAllowedError)  
Raised when an operation is not permitted in the client's current state.

[errors.ListmonkFileNotFoundError](errors.ListmonkFileNotFoundError.md#listmonk.errors.ListmonkFileNotFoundError)  
Raised when a local file referenced for upload (e.g. a transactional email attachment) cannot be found.
