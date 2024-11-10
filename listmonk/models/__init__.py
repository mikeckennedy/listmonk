import datetime
import enum
from typing import Optional, Any

import pydantic
from pydantic import BaseModel, field_serializer, field_validator


class SubscriberStatuses(enum.StrEnum):
    enabled = 'enabled'
    disabled = 'disabled'
    blocklisted = 'blocklisted'


class SubscriberStatus(BaseModel):
    unconfirmed_count: Optional[int] = pydantic.Field(alias='unconfirmed', default=None)


class MailingList(BaseModel):
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
    id: int
    email: str
    name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    uuid: Optional[str] = None
    lists: list[dict] = pydantic.Field(default_factory=list)
    attribs: dict[str, Any] = pydantic.Field(default_factory=dict)
    status: Optional[str] = None

    @field_serializer('created_at', 'updated_at')
    def serialize_date_times(self, fld: datetime, _info):
        formatted_string = fld.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        return formatted_string

    @field_serializer('lists')
    def serialize_lists(self, fld: list[int] | set[int], _info):
        return [int(i) for i in fld]


class CreateSubscriberModel(BaseModel):
    email: str
    name: str
    status: str
    lists: list[int] = pydantic.Field(default_factory=list)
    preconfirm_subscriptions: bool
    attribs: dict = pydantic.Field(default_factory=dict)


class Campaign(BaseModel):
    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    views: int
    clicks: int
    lists: list[dict] = pydantic.Field(default_factory=list)
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
    headers: list[dict] = pydantic.Field(default_factory=dict)


class CreateCampaignModel(BaseModel):
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
    template_id: int
    tags: list[str] = pydantic.Field(default_factory=list)
    headers: list[dict] = pydantic.Field(default_factory=dict)

    @field_serializer('send_at')
    def serialize_date_times(self, fld: datetime, _info):
        if fld:
            # formatted_string = fld.astimezone().strftime('%Y-%m-%dT%H:%M:%SZ')
            formatted_string = fld.astimezone().isoformat()
            return formatted_string
        return None


class UpdateCampaignModel(CreateCampaignModel):
    @field_validator('lists', mode='before')
    def serialize_lists(cls, fld):
        """

        Since we are passing a campaign object to our update method the campaign.lists is a dict and needs to be
        converted to a list of int's

        This method serializes a list by converting each item to integer IDs
        if the item is a dictionary with a key 'id'.

        Parameters:
            cls: The class where the method is defined.
            fld: The list to be serialized.

        Return:
            A new list with items converted to integer IDs if they are dictionaries with a key 'id',
            otherwise returns the original list.

        """
        if isinstance(fld, list):
            # Convert each item to integer IDs if it's a dictionary with 'id'
            return [item['id'] if isinstance(item, dict) else item for item in fld]
        return fld

    @field_validator('send_at', mode='before')
    def serialize_send_at(cls, fld: datetime.datetime):
        """

        Serialize the provided datetime field to prepare for sending, considering the specified send_at time.
        If send_at is in the past then the update will fail, so we check if it is in the past and if it is we turn off
        the campaign scheduled send time.
        Parameters:
            fld (datetime.datetime): The datetime field to be serialized.

        Returns:
            datetime.datetime: Returns the serialized datetime field or None if the provided field is in the past.

        """
        if isinstance(fld, datetime.datetime):
            now = datetime.datetime.now(datetime.timezone.utc)
            if fld < now:
                return None
        return fld


class CampaignPreview(BaseModel):
    preview: Optional[str] = None
