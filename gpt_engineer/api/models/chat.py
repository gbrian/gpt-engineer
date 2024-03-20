from __future__ import annotations
from pydantic import BaseModel

class Chat(BaseModel):
    id: str
    messages: List[Message]

    def md_serialize(self):
        return "\n".join(
            [
                "[[CHAT]]",
                f"[[{self.id}]]"
            ] + [m.md_serialize() for m in self.messages]
        )
    @classmethod
    def md_deserialize(cls, content: str):
        lines = content.split("\n")
        assert lines[0] == "[[CHAT]]"
        chat = Chat()
        chat.id = lines[1]
        chat.messages = [Message.md_deserialize(msg) for msg in "\n".join(lines[2:]).split("[[MESSAGE]]")]
        return chat