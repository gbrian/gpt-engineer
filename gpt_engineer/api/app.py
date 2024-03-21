import time
import logging

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from gpt_engineer.api.model import (
    Chat,
    Settings,
    KnowledgeReloadPath,
    KnowledgeSearch,
    KnowledgeDeleteSources
)
from gpt_engineer.api.app_service import clarify_business_request

from gpt_engineer.core.settings import GPTEngineerSettings 
from gpt_engineer.core import build_dbs, build_ai
from gpt_engineer.core.dbs import DBs

from gpt_engineer.core.step.chat import ai_chat
from gpt_engineer.api.engine import (
    select_afefcted_files_from_knowledge, 
    improve_existing_code,
    check_knowledge_status,
    run_edits,
    create_project
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
            logging.info(f"Request {request.url}")
            gpteng_path = request.query_params.get("gpteng_path")
            settings = None
            if not gpteng_path:
                raise ValueError('Missing gpteng_path')
            try:
                settings = GPTEngineerSettings.from_project(gpteng_path)
                logging.info(f"Request settings {settings.__dict__}")
            except:
                pass
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

        @app.post("/api/knowledge/delete")
        def knowledge_reload_path(knowledgeDeleteSources: KnowledgeDeleteSources, request: Request):
            args = request.state.settings
            dbs = self.get_dbs(args)
            dbs.knowledge.delete_documents(sources=knowledgeDeleteSources.sources)
            return { "ok": 1 }

        @app.post("/api/knowledge/reload-search")
        def knowledge_reload_path(knowledgeSearch: KnowledgeSearch, request: Request):
            args = request.state.settings
            dbs = self.get_dbs(args)
            documents = []
            if knowledgeSearch.search_type == "embeddings":
                documents = dbs.knowledge.search(knowledgeSearch.search_term)
            if knowledgeSearch.search_type == "source":
                documents = dbs.knowledge.search_in_source(knowledgeSearch.search_term)
            return { "documents": documents }

        @app.get("/api/knowledge/status")
        def knowledge_status(request: Request):
            args = request.state.settings
            dbs = self.get_dbs(args)
            return check_knowledge_status(dbs=dbs)

        @app.post("/api/chat")
        def chat(chat: Chat, request: Request):
            settings = request.state.settings
            dbs = self.get_dbs(settings)
            ai = self.get_ai(settings)
            # Perform search on Knowledge using the input
            # Return the search results as response
            user_input = chat.messages[-1].content
            messages = [m.content for m in chat.messages[:-1] if not hasattr(m, "hide")]
            response, documents = ai_chat(ai=ai, dbs=dbs, user_input=user_input, messages=messages, score=float(settings.knowledge_context_cutoff_relevance_score))
            return {
              "message": response,
              "search_results": documents
            }

        @app.post("/api/run/improve")
        def run_improve(chat: Chat, request: Request):
            settings = request.state.settings
            dbs = self.get_dbs(settings)
            ai = self.get_ai(settings)
            # Perform search on Knowledge using the input
            # Return the search results as response
            messages, edits, errors = improve_existing_code(ai=ai, dbs=dbs, chat=chat, settings=settings)
            return {
              "messages": messages,
              "edits": edits,
              "error": errors
            }

        @app.post("/api/run/edit")
        def run_edit(chat: Chat, request: Request):
            args = request.state.settings
            dbs = self.get_dbs(args)
            ai = self.get_ai(args)
            # Perform search on Knowledge using the input
            # Return the search results as response
            message, errors = run_edits(ai=ai, dbs=dbs, chat=chat)
            return {
              "messages": chat.messages + [{ "role": "assistant", "content": message }],
              "errors": errors
            }

        @app.get("/api/settings")
        def settings_check(request: Request):
            settings = request.state.settings
            return GPTEngineerSettings.from_project(settings.gpteng_path).__dict__

        @app.put("/api/settings")
        async def save_settings(request: Request):
            settings = await request.json()
            GPTEngineerSettings.from_json(settings).save_project()
            
            return settings_check(request)

        @app.get("/api/project/create")
        def project_create(request: Request):
            settings = request.state.settings
            if not settings:
                gpteng_path = request.query_params.get("gpteng_path")
                settings = GPTEngineerSettings()
                settings.gpteng_path = gpteng_path
                settings.project_path = gpteng_path
            create_project(settings=settings)
            return "ok"


        return app
