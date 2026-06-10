import datetime
from typing import Any, Optional

import pydantic
from pydantic import BaseModel, field_serializer, field_validator
from strenum import LowercaseStrEnum


class SubscriberStatuses(LowercaseStrEnum):
    """The global status of a subscriber on the Listmonk instance.

    Attributes:
        enabled: The subscriber is active and will receive campaigns.
        disabled: The subscriber is paused and will not receive campaigns.
        blocklisted: The subscriber has been blocked and will not receive any mail.
    """

    enabled = 'enabled'
    disabled = 'disabled'
    blocklisted = 'blocklisted'


class SubscriberStatus(BaseModel):
    """A breakdown of subscriber counts by subscription status for a mailing list.

    Attributes:
        unconfirmed_count: The number of subscriptions still awaiting double opt-in
            confirmation (read from the API's ``unconfirmed`` field).
    """

    unconfirmed_count: Optional[int] = pydantic.Field(alias='unconfirmed', default=None)


class MailingList(BaseModel):
    """A mailing list on the Listmonk instance.

    Attributes:
        id: The numeric list ID assigned by Listmonk.
        created_at: When the list was created.
        updated_at: When the list was last modified, if ever.
        uuid: The globally unique identifier for the list.
        name: The human-readable list name.
        type: The list visibility, typically ``public`` or ``private``.
        optin: The opt-in mode, either ``single`` or ``double``.
        tags: Arbitrary labels attached to the list.
        description: A free-text description of the list.
        subscriber_count: The total number of subscribers on the list.
        subscriber_statuses: A breakdown of subscriber counts by subscription status.
    """

    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    uuid: str
    name: Optional[str] = None
    type: Optional[str] = None
    optin: Optional[str] = None
    tags: list[str]
    description: Optional[str] = None
    subscriber_count: Optional[int] = None
    subscriber_statuses: Optional[SubscriberStatus] = None


class Subscriber(BaseModel):
    """A subscriber (contact) on the Listmonk instance.

    Attributes:
        id: The numeric subscriber ID assigned by Listmonk.
        email: The subscriber's email address (their primary identifier).
        name: The subscriber's display name, if provided.
        created_at: When the subscriber was created.
        updated_at: When the subscriber was last modified, if ever.
        uuid: The globally unique identifier for the subscriber.
        lists: The lists this subscriber belongs to, each as a dict describing the
            membership (list id, subscription status, and so on). Serialization via
            ``model_dump()`` emits plain list IDs.
        attribs: Arbitrary custom attributes stored against the subscriber.
        status: The subscriber's global status, e.g. ``enabled``, ``disabled``, or ``blocklisted``.
    """

    id: int
    email: str
    name: Optional[str] = None
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    uuid: Optional[str] = None
    lists: list[dict[str, Any]] = pydantic.Field(default_factory=list)
    attribs: dict[str, Any] = pydantic.Field(default_factory=dict)
    status: Optional[str] = None

    @field_serializer('created_at', 'updated_at')
    def serialize_date_times(self, fld: Optional[datetime.datetime], _info: Any) -> Optional[str]:
        if fld is None:
            return None
        formatted_string = fld.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        return formatted_string

    @field_serializer('lists')
    def serialize_lists(self, fld: list[dict[str, Any] | int] | set[int], _info: Any) -> list[int]:
        return [int(i['id']) if isinstance(i, dict) else int(i) for i in fld]


class CreateSubscriberModel(BaseModel):
    """
    The payload used to create a new subscriber.

    This is the raw request body sent to Listmonk. The higher-level
    ``create_subscriber`` helper populates it (always sending ``status='enabled'``),
    and ``update_subscriber`` reuses it as the full PUT body when updating an
    existing subscriber (with the caller-supplied status).

    Attributes:
        email: The email address for the new subscriber (required).
        name: The subscriber's display name, if any.
        status: The initial global status (required), e.g. ``enabled``, ``disabled``,
            or ``blocklisted``.
        lists: The IDs of the lists to subscribe this person to. Defaults to an empty list.
        preconfirm_subscriptions: Required flag; when ``True``, mark the new subscriptions as
            confirmed immediately (skipping double opt-in confirmation emails).
        attribs: Arbitrary custom attributes to store against the subscriber. Defaults to an empty dict.
    """

    email: str
    name: Optional[str] = None
    status: str
    lists: list[int] = pydantic.Field(default_factory=list)
    preconfirm_subscriptions: bool
    attribs: dict[str, Any] = pydantic.Field(default_factory=dict)


class Campaign(BaseModel):
    """An email campaign on the Listmonk instance.

    Attributes:
        id: The numeric campaign ID assigned by Listmonk.
        created_at: When the campaign was created.
        updated_at: When the campaign was last modified, if ever.
        views: The number of times the campaign has been opened/viewed.
        clicks: The number of link clicks recorded for the campaign.
        lists: The target lists for the campaign, each as a dict describing the list.
        started_at: When sending began, if the campaign has started.
        to_send: The total number of recipients the campaign will be sent to.
        sent: The number of messages sent so far.
        uuid: The globally unique identifier for the campaign.
        name: The internal campaign name.
        type: The campaign type, e.g. ``regular`` or ``optin``.
        subject: The email subject line.
        from_email: The sender (From) address.
        body: The campaign body in the configured content type.
        altbody: The optional plain-text alternative body for multipart HTML emails.
        send_at: The scheduled send time, if the campaign is scheduled.
        status: The campaign status, e.g. ``draft``, ``scheduled``, ``running``,
            ``paused``, ``cancelled``, or ``finished``.
        content_type: The body format, e.g. ``richtext``, ``html``, ``markdown``, or ``plain``.
        tags: Arbitrary labels attached to the campaign.
        template_id: The ID of the template used to render the campaign.
        messenger: The delivery channel, typically ``email``.
        headers: Custom email headers to include, each as a single-entry dict.
        media: The media files attached to the campaign, each as a dict describing
            the file (id, filename, and so on), or ``None`` if there are none.
    """

    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    views: int
    clicks: int
    lists: list[dict[str, Any]] = pydantic.Field(default_factory=list)
    started_at: Optional[datetime.datetime] = None
    to_send: int
    sent: int
    uuid: str
    name: Optional[str] = None
    type: Optional[str] = None
    subject: Optional[str] = None
    from_email: Optional[str] = None
    body: Optional[str] = None
    altbody: Optional[str] = None
    send_at: Optional[datetime.datetime] = None
    status: Optional[str] = None
    content_type: Optional[str] = None
    tags: list[str] = pydantic.Field(default_factory=list)
    template_id: int
    messenger: Optional[str] = None
    headers: list[dict[str, Optional[str]]] = pydantic.Field(default_factory=list)
    media: Optional[list[dict[str, Any]]] = None


class CreateCampaignModel(BaseModel):
    """
    The payload used to create a new campaign.

    This is the raw request body sent to Listmonk; the higher-level
    ``create_campaign`` helper validates that name and subject are present and
    defaults the target list to ``{1}`` before populating this model.

    Attributes:
        name: The internal campaign name.
        subject: The email subject line.
        lists: The IDs of the lists to send the campaign to. Defaults to an empty list.
        from_email: The sender (From) address. Omit to use the instance default.
        type: The campaign type, e.g. ``regular`` or ``optin``.
        content_type: The body format, e.g. ``richtext``, ``html``, ``markdown``, or ``plain``.
        body: The campaign body in the configured content type.
        altbody: The optional plain-text alternative body for multipart HTML emails.
        send_at: The scheduled send time, if the campaign should be scheduled. Serialized to
            an ISO-8601 string (or ``None``) when sent.
        messenger: The delivery channel, typically ``email``.
        template_id: The ID of the template used to render the campaign. Required field that
            may be ``None`` (it has no default and must be supplied explicitly).
        tags: Arbitrary labels to attach to the campaign. Defaults to an empty list.
        headers: Custom email headers to include, each as a single-entry dict. Defaults to an empty list.
        media: The IDs of uploaded media files to attach to the campaign. Defaults to an empty list.
    """

    name: Optional[str] = None
    subject: Optional[str] = None
    lists: list[int] = pydantic.Field(default_factory=list)
    from_email: Optional[str] = None
    type: Optional[str] = None
    content_type: Optional[str] = None
    body: Optional[str] = None
    altbody: Optional[str] = None
    send_at: Optional[datetime.datetime] = None
    messenger: Optional[str] = None
    template_id: Optional[int]
    tags: list[str] = pydantic.Field(default_factory=list)
    headers: list[dict[str, Optional[str]]] = pydantic.Field(default_factory=list)
    media: list[int] = pydantic.Field(default_factory=list)

    @field_serializer('send_at')
    def serialize_date_times(self, fld: datetime.datetime, _info: Any) -> Optional[str]:
        if fld:
            formatted_string = fld.astimezone().isoformat()
            return formatted_string
        return None


class UpdateCampaignModel(CreateCampaignModel):
    """The payload used to update an existing campaign.

    Shares all fields with ``CreateCampaignModel``. As a safeguard, a ``send_at``
    value that is already in the past is dropped (set to ``None``) before sending,
    so that updating a campaign does not fail on a stale scheduled time.
    """

    # noinspection PyMethodParameters
    @field_validator('send_at', mode='before')
    def validate_send_at(cls, fld: datetime.datetime) -> Optional[datetime.datetime]:
        """
        Drop a send_at value that is already in the past.

        Listmonk rejects updates whose scheduled send time has passed, so a past
        send_at is replaced with None (unscheduling the campaign).

        Args:
            fld: The incoming send_at value.

        Returns:
            The original datetime, or None if it is in the past.
        """
        if isinstance(fld, datetime.datetime):  # type: ignore
            now = datetime.datetime.now(datetime.timezone.utc)
            if fld < now:
                return None
        return fld


class CampaignPreview(BaseModel):
    """A rendered preview of a campaign.

    Attributes:
        preview: The rendered HTML preview of the campaign body.
    """

    preview: Optional[str] = None


class Template(BaseModel):
    """An email template on the Listmonk instance.

    Attributes:
        id: The numeric template ID assigned by Listmonk.
        created_at: When the template was created.
        updated_at: When the template was last modified, if ever.
        name: The template name.
        subject: The default subject line for the template, if any.
        body: The template body markup.
        type: The template type, e.g. ``campaign`` or ``tx`` (transactional).
        is_default: Whether this is the default template for its type.
    """

    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    type: Optional[str] = None
    is_default: Optional[bool] = None


class CreateTemplateModel(BaseModel):
    """
    The payload used to create a new template.

    Attributes:
        name: The template name.
        subject: The default subject line for the template, if any.
        body: The template body markup.
        type: The template type, e.g. ``campaign`` or ``tx`` (transactional).
        is_default: Whether the new template should become the default for its type. Defaults to ``False``.
    """

    name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    type: Optional[str] = None
    is_default: Optional[bool] = False


class TemplatePreview(BaseModel):
    """A rendered preview of a template.

    Attributes:
        preview: The rendered HTML preview of the template, using lorem-ipsum sample content.
    """

    preview: Optional[str] = None


class Media(BaseModel):
    """A file uploaded to the Listmonk media library.

    Attributes:
        id: The numeric media ID assigned by Listmonk. Pass it to ``create_campaign``
            or ``update_campaign`` via ``media_ids`` to attach the file to a campaign.
        uuid: The globally unique identifier for the media file.
        filename: The name the file was stored under.
        content_type: The MIME type of the file, if reported by the server.
        created_at: When the file was uploaded.
        uri: The server path the uploaded file is served from.
        thumb_uri: The server path of the generated thumbnail, if any.
    """

    id: int
    uuid: str
    filename: Optional[str] = None
    content_type: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    uri: Optional[str] = None
    thumb_uri: Optional[str] = None
