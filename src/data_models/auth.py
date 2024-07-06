"""This module contains models that define input / output of Auth Controller."""
from datetime import datetime
from typing import List

from pydantic import BaseModel, constr

from config.project_setting import security_config


class TokenData(BaseModel):
    """A class to represent token data."""
    sub: str
    scopes: List[str] = []
    account: str
    user_id: str
    iat: datetime
    exp: datetime


class ChangePasswordRequest(BaseModel):
    """A class to represent change password request."""
    current_password: str
    new_password: constr(regex=security_config.password_rule_regex)
