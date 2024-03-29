import pytest
import logging

from gpt_engineer.core.settings import GPTEngineerSettings
from gpt_engineer.core.chat_manager import ChatManager
from gpt_engineer.api.model import Chat, Message

gpteng_path = path = "tests/.gpteng"

MESSAGES = [
    Message(role="user", content="my message", hide=False),
    Message(role="assistant", content="Hi there!", hide=True)
]
EXPECTED_CHAT = Chat(
    name="new cahe", id=10, role="no-role", messages=MESSAGES
)
EXPECTED_CHAT_CONTENT = "\n".join([
                    '[[{"id": "10", "name": "new cahe", "profile": ""}]]',
                    '[[{"role": "user", "hide": false}]]',
                    'my message',
                    '[[{"role": "assistant", "hide": true}]]',
                    'Hi there!'
                    ])

def get_chat_manager():
    settings = GPTEngineerSettings(gpteng_path="")
    return ChatManager(settings)

def test_chat_serialization():
    chat_manager = get_chat_manager()
    content = chat_manager.serialize_chat(EXPECTED_CHAT)
    
    assert content == EXPECTED_CHAT_CONTENT

def test_chat_deserialization():
    chat_manager = get_chat_manager()
    chat = chat_manager.deserialize_chat(EXPECTED_CHAT_CONTENT)
    
    assert chat.id == EXPECTED_CHAT.id
    assert chat.name == EXPECTED_CHAT.name
    assert chat.profile == EXPECTED_CHAT.profile
    assert len(chat.messages) == len(EXPECTED_CHAT.messages)
    assert chat.messages[0] == EXPECTED_CHAT.messages[0]
    assert chat.messages[1] == EXPECTED_CHAT.messages[1]

def test_chat_list():
    settings = GPTEngineerSettings(gpteng_path="")
    chat_manager = ChatManager(settings)

    
    chat_manager