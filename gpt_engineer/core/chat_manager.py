import logging
import pathlib
import os
import json
from gpt_engineer.core.settings import GPTEngineerSettings

from gpt_engineer.api.model import Chat, Message

class ChatManager:
    def __init__(self, settings: GPTEngineerSettings):
        self.settings = settings
        self.chat_path = f"{settings.gpteng_path}/tasks"
        os.makedirs(self.chat_path, exist_ok=True)

    def list_chats(self):
        path = self.chat_path
        file_paths = [os.path.basename(str(file_path)) for file_path in pathlib.Path(path).rglob("*")]
        return file_paths

    def save_chat(self, chat: Chat):
        chat_file = f"{self.chat_path}/{chat.name}"
        logging.info(f"Save chat {chat}")
        with open(chat_file, 'w') as f:
            chat_content = self.serialize_chat(chat)
            logging.info(f"serialize_chat: {chat_content}")
            f.write(chat_content)

    def load_chat(self, chat_name):
        chat_file = f"{self.chat_path}/{chat_name}"
        with open(chat_file, 'r') as f:
            return self.deserialize_chat(content=f.read())

    def serialize_chat(self, chat: Chat):
        chat_json = { **chat.__dict__ }
        del chat_json["messages"]  
        header = f"[[{json.dumps(chat_json)}]]"
        def serialize_message(message):
            message_json = { **message.__dict__ }
            del message_json["content"]
            return "\n".join([
                    f"[[{json.dumps(message_json)}]]",
                    message.content
                ]
            )
        messages = [serialize_message(message) for message in chat.messages]
        chat_content = "\n".join([header] + messages)
        return chat_content

    def deserialize_chat(self, content) -> Chat:
        lines = content.split("\n")
        chat_json = json.loads(lines[0][2:-2])
        chat = Chat(**chat_json)
        chat.messages = []
        chat_message = None
        for line in lines[1:]:
            if line.startswith("[[{") and line.endswith("}]]"):
                message_json = json.loads(line[2:-2])
                chat_message = Message(role=message_json["role"], hide=message_json.get("hide") or False)
                chat_message.content = ""
                chat.messages.append(chat_message)
                continue
            chat_message.content = line if not chat_message.content else f"{chat_message.content}\n{line}"
        return chat