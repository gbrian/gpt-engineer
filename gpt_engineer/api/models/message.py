from __future__ import annotations
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str
    time: int

    def md_serialize(self):
        return "\n".join([
            "[[MESSAGE]]",
            f"[[{self.role}]]",
            f"[[{self.time}]]",
            self.content
        ])

    @classmethod
    def md_serialize(cls, content: str):
        lines = content.split("\n")
        assert lines[0] == "[[MESSAGE]]"
        message = Message()
        message.role = lines[1][2:-2]
        message.time = int(lines[2][2:-2])
        message.content = "\n".join(lines[3:])
        return message