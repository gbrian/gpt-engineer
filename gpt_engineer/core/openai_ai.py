from typing import Union
from openai import OpenAI
from openai.types.chat.chat_completion_system_message_param import ChatCompletionSystemMessageParam
from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam

from gpt_engineer.settings import OPENAI_API_KEY, OPENAI_API_BASE, MODEL, TEMPERATURE
from langchain.schema import (
    AIMessage,
    HumanMessage
)

class OpenAI_AI:
    def __init__(self):
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_API_BASE
        )

    def convert_message(self, gpt_message: Union[AIMessage, HumanMessage]): 
        if gpt_message.type == "ia":
            return { "content": gpt_message.content, "role": "system" }
        return { "content": gpt_message.content, "role": "user" }

    def chat_completions(self, messages, config={}):
        openai_messages = [self.convert_message(msg) for msg in messages]
        response = self.client.chat.completions.create(
            model=config.get("model", MODEL),
            temperature=config.get("temperature", TEMPERATURE),
            messages=openai_messages,
            stream=True
        )
        callbacks = config.get("callbacks", None)
        content_parts = []
        for chunk in response:
            chunk_content = chunk.choices[0].delta.content
            if not chunk_content:
                continue

            content_parts.append(chunk_content)
            if callbacks:
                for cb in callbacks:
                    cb.on_llm_new_token(chunk_content)

        return AIMessage(content="".join(content_parts))

