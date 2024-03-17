from __future__ import annotations
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str