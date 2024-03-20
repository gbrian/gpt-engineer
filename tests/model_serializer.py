import logging
from gpt_engineer.api.models import Chat, Message

def test_serialize_chat():
  chat = Chat(id="MY_ID")
  chat.messages = [
    Message(role="user", content="User content"),
    Message(role="assistant", content="Assistant content"),
  ]

  md_chat = chat.md_serialize()
  logging.info(f"Chat serialized {md_chat}")