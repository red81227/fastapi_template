"""This module contains classes that define input / output of User Controller."""
from typing import Optional
from pydantic import BaseModel
from src.data_models.common import CommonModel

class User(CommonModel):
    """A class to represent user."""
    account: str
    # password: str
    email_address: str
    # some alert settings
    authority: str
    additional_info: Optional[str] = ""


class CreateUserRequest(BaseModel):
    """A class to represent create user request."""
    account: str
    email_address: str
    additional_info: Optional[str] = ""

class UpdateUserRequest(BaseModel):
    """A class to represent update user request."""
    account: str
    email_address: str
    additional_info: Optional[str] = ""