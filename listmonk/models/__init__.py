import pydantic
from pydantic import BaseModel


class SubscriberStatus(BaseModel):
    unconfirmed_count: int = pydantic.Field(alias="unconfirmed")


class MailingList(BaseModel):
    id: int
    created_at: str
    updated_at: str
    uuid: str
    name: str
    type: str
    optin: str
    tags: list[str]
    description: str
    subscriber_count: int
    subscriber_statuses: SubscriberStatus
