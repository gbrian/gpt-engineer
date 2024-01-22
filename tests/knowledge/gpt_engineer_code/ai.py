
from __future__ import annotations

import json
import logging
import os

from typing import List, Optional, Union

import backoff
import openai

import hashlib

from gpt_engineer.core.token_usage import TokenUsageLog

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    messages_from_dict,
    messages_to_dict,
)

# Type hint for a chat message
Message = Union[AIMessage, HumanMessage, SystemMessage]

# Set up logging
logger = logging.getLogger(__name__)


class AI:

    def __init__(
        self, model_name="gpt-4", temperature=0.1, azure_endpoint="", cache=None
    ):
        self.temperature = temperature
        self.azure_endpoint = azure_endpoint
        self.model_name = self._check_model_access_and_fallback(model_name)

        self.llm = self._create_chat_model()
        self.token_usage_log = TokenUsageLog(model_name)

        self.cache = cache

        logger.debug(f"Using model {self.model_name}")

    def start(self, system: str, user: str, step_name: str) -> List[Message]:
        

        messages: List[Message] = [
            SystemMessage(content=system),
            HumanMessage(content=user),
        ]
        return self.next(messages, step_name=step_name)

    def next(
        self,
        messages: List[Message],
        prompt: Optional[str] = None,
        *,
        step_name: str,
    ) -> List[Message]:
        
        if prompt:
            messages.append(HumanMessage(content=prompt))

        logger.debug(f"Creating a new chat completion: {messages}")

        response = None
        md5Key = messages_md5(messages) if self.cache else None
        if self.cache and md5Key in self.cache:
            response = AIMessage(content=json.loads(self.cache[md5Key])["content"])

        if not response:
            callbacks = [StreamingStdOutCallbackHandler()]
            response = self.backoff_inference(messages, callbacks)
            if self.cache:
                self.cache[md5Key] = json.dumps(
                    {
                        "messages": serialize_messages(messages),
                        "content": response.content,
                    }
                )
        else:
            logger.debug(f"Response from cache: {messages} {response}")

        self.token_usage_log.update_log(
            messages=messages, answer=response.content, step_name=step_name
        )
        messages.append(response)
        logger.debug(f"Chat completion finished: {messages}")

        return messages

    @backoff.on_exception(
        backoff.expo, openai.error.RateLimitError, max_tries=7, max_time=45
    )
    def backoff_inference(self, messages, callbacks):
        
        return self.llm(messages, callbacks=callbacks)  # type: ignore

    @staticmethod
    def serialize_messages(messages: List[Message]) -> str:
        try:
            return json.dumps(messages_to_dict(messages))
        except Exception as ex:
            logger.error(f"serialize_messages error: {messages} {ex}")
            raise ex

    @staticmethod
    def deserialize_messages(jsondictstr: str) -> List[Message]:
        data = json.loads(jsondictstr)
        # Modify implicit is_chunk property to ALWAYS false
        # since Langchain's Message schema is stricter
        prevalidated_data = [
            {**item, "data": {**item["data"], "is_chunk": False}} for item in data
        ]
        return list(messages_from_dict(prevalidated_data))  # type: ignore

    def _check_model_access_and_fallback(self, model_name) -> str:
        try:
            openai.Model.retrieve(model_name)
        except openai.InvalidRequestError:
            print(
                f"Model {model_name} not available for provided API key. Reverting "
                "to gpt-3.5-turbo. Sign up for the GPT-4 wait list here: "
                "https://openai.com/waitlist/gpt-4-api\n"
            )
            return "gpt-3.5-turbo"

        return model_name

    def _create_chat_model(self) -> BaseChatModel:
        if self.azure_endpoint:
            return AzureChatOpenAI(
                openai_api_base=self.azure_endpoint,
                openai_api_version=os.getenv("OPENAI_API_VERSION", "2023-05-15"),
                deployment_name=self.model_name,
                openai_api_type="azure",
                streaming=True,
            )

        return ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            streaming=True,
            client=openai.ChatCompletion,
        )


def serialize_messages(messages: List[Message]) -> str:
    return AI.serialize_messages(messages)


def messages_md5(messages: List[Message]):
    messageaStr = "".join(map(lambda x: x.content, messages))
    return str(hashlib.md5(messageaStr.encode("utf-8")).hexdigest())
