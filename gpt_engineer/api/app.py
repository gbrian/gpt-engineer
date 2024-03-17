from fastapi import FastAPI
from gpt_engineer.api.model import ChatMessage, Message
from gpt_engineer.api.app_service import clarify_business_request

from gpt_engineer.core.settings import GPTEngineerSettings 
from gpt_engineer.core import build_dbs, build_ai
from gpt_engineer.core.dbs import DBs

from gpt_engineer.core.step.chat import ai_chat

class GPTEngineerAPI:
    def __init__(self, args: GPTEngineerSettings):
        self.dbs = build_dbs(args)
        self.ai = build_ai(args)

    def start(self):
        app = FastAPI()

        @app.get("/health")
        def health_check():
            return "ok"

        @app.post("/chat")
        def chat(chat_message: ChatMessage):
            # Perform search on Knowledge using the input
            # Return the search results as response
            user_input = chat_message.messages[-1].content
            messages = [m.content for m in chat_message.messages[:-1]]
            response, documents = ai_chat(ai=self.ai, dbs=self.dbs, user_input=user_input, messages=messages)
            return {"message": response, "search_results": documents}

        @app.post("/improve")
        def chat(chat_message: ChatMessage):
            # Perform search on Knowledge using the input
            # Return the search results as response
            user_input = chat_message.messages[-1].content
            messages = [m.content for m in chat_message.messages[:-1]]
            response, documents = ai_chat(ai=self.ai, dbs=self.dbs, user_input=user_input, messages=messages)
            return {"message": response, "search_results": documents}

        return app
