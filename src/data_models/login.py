"""This module contains models that define input / output of Login Endpoint."""
from pydantic import BaseModel
from fastapi import Form

class LoginResponse(BaseModel):
    """A class to represent login response."""
    access_token: str
    token_type: str
