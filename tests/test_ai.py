import json

from gpt_engineer.core.ai import AI, messages_md5
from gpt_engineer.core.db import DB
from gpt_engineer.core.token_usage import TokenUsage
from langchain.chat_models.fake import FakeListChatModel
from langchain.chat_models.base import BaseChatModel
from langchain.schema import AIMessage


def mock_create_chat_model(self) -> BaseChatModel:
    return FakeListChatModel(responses=["response1", "response2", "response3"])


def mock_check_model_access_and_fallback(self, model_name):
    return model_name


def test_start(monkeypatch):
    # arrange
    monkeypatch.setattr(
        AI, "_check_model_access_and_fallback", mock_check_model_access_and_fallback
    )
    monkeypatch.setattr(AI, "_create_chat_model", mock_create_chat_model)

    ai = AI("gpt-4")

    # act
    response_messages = ai.start("system prompt", "user prompt", "step name")

    # assert
    assert response_messages[-1].content == "response1"


def test_next(monkeypatch):
    # arrange
    monkeypatch.setattr(
        AI, "_check_model_access_and_fallback", mock_check_model_access_and_fallback
    )
    monkeypatch.setattr(AI, "_create_chat_model", mock_create_chat_model)

    ai = AI("gpt-4")
    response_messages = ai.start("system prompt", "user prompt", "step name")

    # act
    response_messages = ai.next(
        response_messages, "next user prompt", step_name="step name"
    )

    # assert
    assert response_messages[-1].content == "response2"


def test_ai_cache(monkeypatch):
    cache = DB(".cache")
    # arrange
    monkeypatch.setattr(
        AI, "_check_model_access_and_fallback", mock_check_model_access_and_fallback
    )
    monkeypatch.setattr(AI, "_create_chat_model", mock_create_chat_model)

    ai = AI("gpt-4", cache=cache)
    response_messages = ai.start("system prompt", "user prompt", "step name")

    aiMessage = AIMessage(content="next user prompt")
    messages = response_messages + [aiMessage]
    md5Messages = messages_md5(messages)

    # act
    response_messages = ai.next(
        response_messages, "next user prompt", step_name="step name"
    )

    # assert
    assert json.loads(cache[md5Messages])["content"] == "response2"


def test_token_logging(monkeypatch):
    # arrange
    monkeypatch.setattr(
        AI, "_check_model_access_and_fallback", mock_check_model_access_and_fallback
    )
    monkeypatch.setattr(AI, "_create_chat_model", mock_create_chat_model)

    ai = AI("gpt-4")

    # act
    response_messages = ai.start("system prompt", "user prompt", "step name")
    usageCostAfterStart = ai.token_usage_log.usage_cost()
    ai.next(response_messages, "next user prompt", step_name="step name")
    usageCostAfterNext = ai.token_usage_log.usage_cost()

    # assert
    assert usageCostAfterStart > 0
    assert usageCostAfterNext > usageCostAfterStart