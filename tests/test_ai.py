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

def test_start_with_max_response_length_none(monkeypatch):
    # arrange
    monkeypatch.setattr(
        AI, "_check_model_access_and_fallback", mock_check_model_access_and_fallback
    )
    monkeypatch.setattr(AI, "_create_chat_model", mock_create_chat_model)

    ai = AI("gpt-4")

    # act
    response_messages = ai.start("system prompt", "user prompt", "step name", max_response_length=None)

    # assert
    assert response_messages[-1].content == "response1"

def test_start_with_max_response_length_shorter(monkeypatch):
    # arrange
    monkeypatch.setattr(
        AI, "_check_model_access_and_fallback", mock_check_model_access_and_fallback
    )
    monkeypatch.setattr(AI, "_create_chat_model", mock_create_chat_model)

    ai = AI("gpt-4")
    # Mock response longer than max_response_length to test truncation
    short_response = "short response that is actually quite long"
    max_response_length=3
    # act
    # Adjusting max_response_length to be shorter than the mock response
    response_messages = ai.start("system prompt", "user prompt", "step name", max_response_length=max_response_length)

    # assert
    # Asserting that the response is truncated to the max_response_length
    assert len(response_messages[-1].content) == max_response_length

def test_start_with_max_response_length_longer(monkeypatch):
    # arrange
    monkeypatch.setattr(
        AI, "_check_model_access_and_fallback", mock_check_model_access_and_fallback
    )
    monkeypatch.setattr(AI, "_create_chat_model", mock_create_chat_model)

    ai = AI("gpt-4")
    # Mock response shorter than max_response_length to test no truncation
    long_response = "long response"

    # act
    # Adjusting max_response_length to be longer than the mock response
    response_messages = ai.start("system prompt", "user prompt", "step name", max_response_length=len(long_response) + 10)

    # assert
    # Asserting that the full response is returned when max_response_length is longer
    assert response_messages[-1].content == long_response