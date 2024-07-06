"""This module contains models that can transfer data with database."""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, validator

class EntityBaseModel(BaseModel):
    """A class to represent common elements of entities."""
    id: str

    @validator("*", pre=True)
    def uuid_to_str(cls, v):
        # pylint: disable=E0213,R0201
        """Turn UUID items into str."""
        if isinstance(v, UUID):
            return str(v)
        return v

class User(EntityBaseModel):
    """A class to represent an User entity."""
    account: str
    hashed_password: Optional[str]
    email_address: str
    authority: str
    additional_info: Optional[str] = ""


class TableName:
    """A class to define table names."""
    # pylint: disable=too-few-public-methods
    USERS = "users"
    DEVICES = "devices"
    ROOMS = "rooms"
    ROOM_DEVICE_PAIRS = "room_device_pairs"
    METER_1P = "meter_1p"
    METER_3P = "meter_3p"
    AC = "ac"
    SENSOR = "sensor"
    MODEL = "model"