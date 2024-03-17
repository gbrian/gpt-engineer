import time
from fastapi import FastAPI, Request

from gpt_engineer.api.models.chatmessage import ChatMessage
from gpt_engineer.api.models.message import Message
from gpt_engineer.api.app_service import clarify_business_request

from gpt_engineer.core.settings import GPTEngineerSettings 
from gpt_engineer.core import build_dbs, build_ai
from gpt_engineer.core.dbs import DBs

from gpt_engineer.core.step.chat import ai_chat
from gpt_engineer.api.engine import select_afefcted_files_from_knowledge, improve_existing_code

class GPTEngineerAPI:
    def __init__(self, args: GPTEngineerSettings):
        self.dbs = build_dbs(args)
        self.ai = build_ai(args)

    def start(self):
        app = FastAPI()

        @app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response

        @app.middleware("http")
        async def refresh_knowledge(request: Request, call_next):
            reloaded = self.dbs.knowledge.reload()
            response = await call_next(request)
            response.headers["X-Knowledge-Reloaded"] = str(reloaded) 
            return response

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
            return {
              "message": response,
              "search_results": documents
            }

        @app.post("/improve")
        def chat(chat_message: ChatMessage):
            # Perform search on Knowledge using the input
            # Return the search results as response
            messages, edits, error = improve_existing_code(ai=self.ai, dbs=self.dbs, chat_message=chat_message)
            return {
              "messages": messages,
              "edits": edits,
              "error": error
            }
        return app
