import pytest
from langchain.schema import (
    HumanMessage,
)
from gpt_engineer.core.openai_ai import OpenAI_AI

def test_completion ():
    ai = OpenAI_AI()
    res = ai.chat_completions([HumanMessage(content="Hey, how are you today?")])
    assert res.content