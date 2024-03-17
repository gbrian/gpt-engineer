from __future__ import annotations
from pydantic import BaseModel
from typing import List, Dict
from .choice import Choice

class ChatResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    system_fingerprint: str
    choices: List[Choice]
    usage: Dict[str, int]