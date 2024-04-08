import logging
from typing import Union
from openai import OpenAI
from openai.types.chat.chat_completion_system_message_param import ChatCompletionSystemMessageParam
from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam

from gpt_engineer.core.settings import GPTEngineerSettings
from langchain.schema import (
    AIMessage,
    HumanMessage
)

class OpenAI_AI:
    def __init__(self, settings: GPTEngineerSettings):
        self.settings = settings
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base
        )

    def convert_message(self, gpt_message: Union[AIMessage, HumanMessage]): 
        if gpt_message.type == "ia":
            return { "content": gpt_message.content, "role": "system" }
        return { "content": gpt_message.content, "role": "user" }

    def chat_completions(self, messages, config={}):
        openai_messages = [self.convert_message(msg) for msg in messages]
        response_stream = self.client.chat.completions.create(
            model=config.get("model", self.settings.model),
            temperature=float(config.get("temperature", self.settings.temperature)),
            messages=openai_messages,
            stream=True
        )
        callbacks = config.get("callbacks", None)
        content_parts = []
        for chunk in response_stream:
            chunk_content = chunk.choices[0].delta.content
            if not chunk_content:
                continue

            content_parts.append(chunk_content)
            if callbacks:
                for cb in callbacks:
                    cb.on_llm_new_token(chunk_content)

        response_content = "".join(content_parts)
        logging.debug("\n".join(
            [f"[{message.type}]\n{message.content}" for message in messages] +
            ["[AI]",response_content]
        ))
        return AIMessage(content=response_content)

