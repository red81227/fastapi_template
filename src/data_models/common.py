"""This module contains common models that define input / output of Controllers."""
from enum import Enum
from uuid import uuid1

from pydantic import BaseModel, Field, validator

# from pydantic.types import UUID1
from uuid import UUID


class CommonModel(BaseModel):
    """A class to represent common elements of data models."""
    id: UUID = str(Field(default_factory=uuid1))

class BaseResponse(BaseModel):
    """A class to represent basic response."""
    result: str = "Successful"

class Accuracy(BaseModel):
    """A class to represent accuracy."""
    r_squared: float
    mae: float
    winorized_mse: float
    estimate_start_at: int