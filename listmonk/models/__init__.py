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
    created_at: datetime.datetime
    updated_at: datetime.datetime
    uuid: str
    email: str
    name: str
    attribs: dict[str, typing.Any]
