from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from .message import Message
from .logprobs import Logprobs

class Choice(BaseModel):
    index: int
    message: Message
    logprobs: Optional[Logprobs]
    finish_reason: str