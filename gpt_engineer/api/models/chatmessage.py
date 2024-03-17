from __future__ import annotations
from pydantic import BaseModel
from typing import List
from .message import Message

class ChatMessage(BaseModel):
    messages: List[Message]