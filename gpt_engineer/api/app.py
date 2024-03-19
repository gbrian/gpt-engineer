import time
import logging

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from gpt_engineer.api.models.chatmessage import ChatMessage
from gpt_engineer.api.models.message import Message
from gpt_engineer.api.models.settings import Settings
from gpt_engineer.api.models.knowledge import KnowledgeReloadPath
from gpt_engineer.api.app_service import clarify_business_request

from gpt_engineer.core.settings import GPTEngineerSettings 
from gpt_engineer.core import build_dbs, build_ai
from gpt_engineer.core.dbs import DBs

from gpt_engineer.core.step.chat import ai_chat
from gpt_engineer.api.engine import (
    select_afefcted_files_from_knowledge, 
    improve_existing_code,
    check_knowledge_status,
    run_edits
)

class GPTEngineerAPI:
    def get_dbs(self, args: GPTEngineerSettings):
        return build_dbs(settings=args, ai=build_ai(args))

    def get_ai(self, args: GPTEngineerSettings):
        return build_ai(args)

    def start(self):
        app = FastAPI(
            title="GPTEngineerAPI",
            description="API for GPTEngineer",
            version="1.0",
            openapi_url="/api/openapi.json",
            docs_url="/api/docs",
            redoc_url="/api/redoc",
        )

        app.mount("/static", StaticFiles(directory="gpt_engineer/api/client_chat", html=True), name="client_chat")

        @app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response

        @app.middleware("http")
        async def add_gpt_engineer_settings(request: Request, call_next):
            project_path = request.query_params.get("project_path")
            settings = GPTEngineerSettings.from_env()
            if project_path:
                settings = GPTEngineerSettings.from_project(project_path)
            logging.info(f"Request settings {settings.__dict__}")
            request.state.settings = settings
            response = await call_next(request)
            return response

        @app.get("/api/health")
        def health_check():
            return "ok"

        @app.get("/api/knowledge/reload")
        def knowledge_reload(request: Request):
            args = request.state.settings
            dbs = self.get_dbs(args)
            dbs.knowledge.reload()
            return knowledge_status(request)

        @app.post("/api/knowledge/reload-path")
        def knowledge_reload_path(knowledgeReloadPath: KnowledgeReloadPath, request: Request):
            args = request.state.settings
            dbs = self.get_dbs(args)
            documents = dbs.knowledge.reload_path(knowledgeReloadPath.path)
            return { "doc_count": len(documents) }

        @app.get("/api/knowledge/status")
        def knowledge_status(request: Request):
            args = request.state.settings
            dbs = self.get_dbs(args)
            return check_knowledge_status(dbs=dbs)

        @app.post("/api/chat")
        def chat(chat_message: ChatMessage, request: Request):
            args = request.state.settings
            dbs = self.get_dbs(args)
            ai = self.get_ai(args)
            # Perform search on Knowledge using the input
            # Return the search results as response
            user_input = chat_message.messages[-1].content
            messages = [m.content for m in chat_message.messages[:-1]]
            response, documents = ai_chat(ai=ai, dbs=dbs, user_input=user_input, messages=messages)
            return {
              "message": response,
              "search_results": documents
            }

        @app.post("/api/run/improve")
        def run_improve(chat_message: ChatMessage, request: Request):
            args = request.state.settings
            dbs = self.get_dbs(args)
            ai = self.get_ai(args)
            # Perform search on Knowledge using the input
            # Return the search results as response
            messages, edits, errors = improve_existing_code(ai=ai, dbs=dbs, chat_message=chat_message)
            return {
              "messages": messages,
              "edits": edits,
              "error": errors
            }

        @app.post("/api/run/edit")
        def run_edit(chat_message: ChatMessage, request: Request):
            args = request.state.settings
            dbs = self.get_dbs(args)
            ai = self.get_ai(args)
            # Perform search on Knowledge using the input
            # Return the search results as response
            message, errors = run_edits(ai=ai, dbs=dbs, chat_message=chat_message)
            return {
              "messages": chat_message.messages + [{ "role": "assistant", "content": message }],
              "errors": errors
            }

        @app.get("/api/settings")
        def settings_check(request: Request):
            return request.state.settings.__dict__

        @app.put("/api/settings")
        async def save_settings(request: Request):
            settings = await request.json()
            GPTEngineerSettings.from_json(settings).save_project()
            
            return settings_check(request)

        return app
