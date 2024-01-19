import datetime
import typing

import pydantic
from pydantic import BaseModel


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


class CreateSubscriberModel(BaseModel):
    email: str
    name: str
    status: str
    lists: list[int] = []
    preconfirm_subscriptions: bool
    attribs: dict = {}
