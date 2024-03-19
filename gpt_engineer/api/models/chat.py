from __future__ import annotations
from pydantic import BaseModel

class Chat(BaseModel):
    id: str
    messages: List[Message]