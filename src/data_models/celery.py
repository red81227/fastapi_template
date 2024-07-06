from typing import Optional
from pydantic import BaseModel

class CeleryResponse(BaseModel):
    """A class to represent CeleryResponse."""
    message: str
    task_id: str