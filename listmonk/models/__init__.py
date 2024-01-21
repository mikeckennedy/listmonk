import datetime
import enum
import typing

import pydantic
from pydantic import BaseModel, field_serializer


class SubscriberStatuses(enum.StrEnum):
    enabled = "enabled"
    disabled = "disabled"
    blocklisted = "blocklisted"


class SubscriberStatus(BaseModel):
    unconfirmed_count: int = pydantic.Field(alias="unconfirmed")


class MailingList(BaseModel):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    uuid: str
    name: str
    type: str
    optin: str
    tags: list[str]
    description: str
    subscriber_count: int
    subscriber_statuses: SubscriberStatus


class Subscriber(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    uuid: typing.Optional[str] = None
    lists: list[dict] = []
    attribs: dict[str, typing.Any] = {}
    status: typing.Optional[str] = None

    @field_serializer('created_at', 'updated_at')
    def serialize_date_times(self, fld: datetime, _info):
        formatted_string = fld.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return formatted_string

    @field_serializer('lists')
    def serialize_lists(self, fld: list[int] | set[int], _info):
        return [int(i) for i in fld]


class CreateSubscriberModel(BaseModel):
    email: str
    name: str
    status: str
    lists: list[int] = []
    preconfirm_subscriptions: bool
    attribs: dict = {}
