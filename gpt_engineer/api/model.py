from __future__ import annotations
from pydantic import BaseModel, Field

from typing import List, Dict, Union

from gpt_engineer.core.settings import GPTEngineerSettings

class Message(BaseModel):
    role: str
    content: str

class Chat(BaseModel):
    id: str = Field(default='')
    name: str = Field(default='')
    profile: str = Field(default='')
    messages: List[Message]

class Message(BaseModel):
    role: str
    content: str
    hide: bool = Field(default=False)

class Logprobs(BaseModel):
    tokens: List[str]
    token_logprobs: List[float]
    top_logprobs: List[Dict[str, float]]
    text_offset: List[int]

class Choice(BaseModel):
    index: int
    message: Message
    logprobs: Optional[Logprobs]
    finish_reason: str

class ChatResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    system_fingerprint: str
    choices: List[Choice]
    usage: Dict[str, int]

class KnowledgeReloadPath(BaseModel):
    path: str

class KnowledgeDeleteSources(BaseModel):
    sources: List[str]

class KnowledgeSearch(BaseModel):
    search_term: str
    search_type: str

class Profile(BaseModel):
    name: str
    content: str

class Settings(BaseModel, GPTEngineerSettings):
  pass