import os
import time
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import traceback
for logger_id in [
    'apscheduler.scheduler',
    'apscheduler.executors.default',
    'httpx'
    ]:
    logging.getLogger(logger_id).setLevel(logging.WARNING)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from gpt_engineer.api.model import (
    Chat,
    Message,
    Settings,
    KnowledgeReloadPath,
    KnowledgeSearch,
    KnowledgeDeleteSources,
    Profile,
    Document
)
from gpt_engineer.api.app_service import clarify_business_request

from gpt_engineer.core.settings import GPTEngineerSettings 
from gpt_engineer.core.dbs import DBs
from gpt_engineer.api.profile_manager import ProfileManager
from gpt_engineer.core.chat_manager import ChatManager

from gpt_engineer.api.engine import (
    select_afected_files_from_knowledge, 
    improve_existing_code,
    check_knowledge_status,
    run_edits,
    create_project,
    select_afefcted_documents_from_knowledge,
    check_project_changes,
    reload_knowledge,
    delete_knowledge_source,
    knowledge_search,
    chat_with_project,
    check_project,
    extract_tags,
    get_keywords
)

WATCH_FOLDERS = []
from gpt_engineer.core.scheduler import add_work

def process_projects_changes():
    for gpteng_path in WATCH_FOLDERS:
        try:
            settings = GPTEngineerSettings.from_project(gpteng_path=gpteng_path)
            check_project_changes(settings=settings)
        except Exception as ex:
            logger.exception(f"Processing {gpteng_path} error: {ex}")
            pass

add_work(process_projects_changes)

class GPTEngineerAPI:
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
        @app.on_event("startup")
        def startup_event():
            logger.info("Creating FASTAPI")
        
        @app.exception_handler(Exception)
        async def my_exception_handler(request: Request, ex: Exception):
            return JSONResponse(status_code=500, 
                content=traceback.format_exception(ex))

        @app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            logger.info("FASTAPI::add_process_time_header")
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response

        @app.middleware("http")
        async def add_gpt_engineer_settings(request: Request, call_next):
            logger.info("FASTAPI::add_process_time_header")
            logger.info(f"Request {request.url}")
            gpteng_path = request.query_params.get("gpteng_path")
            settings = None
            if gpteng_path:
                try:
                    settings = GPTEngineerSettings.from_project(gpteng_path)
                    logger.info(f"Request settings {settings.__dict__}")
                except:
                    pass
            request.state.settings = settings
            return await call_next(request)


        @app.get("/api/health")
        def health_check():
            return "ok"

        @app.get("/api/knowledge/reload")
        def knowledge_reload(request: Request):
            settings = request.state.settings
            check_project_changes(settings=settings)
            reload_knowledge(settings=settings)
            return check_knowledge_status(settings=settings)

        @app.post("/api/knowledge/reload-path")
        def knowledge_reload_path(knowledge_reload_path: KnowledgeReloadPath, request: Request):
            settings = request.state.settings
            reload_knowledge(settings=settings, path=knowledge_reload_path.path)
            return check_knowledge_status(settings=settings)

        @app.post("/api/knowledge/delete")
        def knowledge_reload_path(knowledge_delete_sources: KnowledgeDeleteSources, request: Request):
            settings = request.state.settings
            return delete_knowledge_source(settings=settings, sources=knowledge_delete_sources.sources)

        @app.post("/api/knowledge/reload-search")
        def knowledge_search_endpoint(knowledge_search_params: KnowledgeSearch, request: Request):
            settings = request.state.settings
            return knowledge_search(settings=settings, knowledge_search=knowledge_search_params)

        @app.get("/api/knowledge/status")
        def api_knowledge_status(request: Request):
            settings = request.state.settings
            return check_knowledge_status(settings=settings)

        @app.get("/api/chats")
        def list_chats(request: Request):
            settings = request.state.settings
            chat_name = request.query_params.get("chat_name")
            chat_manager = ChatManager(settings=settings)
            if chat_name:
                return chat_manager.load_chat(chat_name=chat_name)
            return chat_manager.list_chats()

        @app.post("/api/chats")
        def chat(chat: Chat, request: Request):
            settings = request.state.settings
            streaming = request.query_params.get("streaming")
            if streaming:
              def doStreaming():
                data_buffer = DataBuffer()
                chat = chat_with_project(settings=settings, chat=chat, use_knowledge=True)
                ChatManager(settings=settings).save_chat(chat) 
              return StreamingResponse()
            else:
              chat = chat_with_project(settings=settings, chat=chat, use_knowledge=True)
              ChatManager(settings=settings).save_chat(chat)
              return chat.messages[-1]

        @app.put("/api/chats")
        def save_chat(chat: Chat, request: Request):
            settings = request.state.settings
            ChatManager(settings=settings).save_chat(chat)
        

        @app.post("/api/run/improve")
        def run_improve(chat: Chat, request: Request):
            settings = request.state.settings
            # Perform search on Knowledge using the input
            # Return the search results as response
            improve_existing_code(chat=chat, settings=settings)
            ChatManager(settings=settings).save_chat(chat)
            return chat

        @app.post("/api/run/edit")
        def run_edit(chat: Chat, request: Request):
            settings = request.state.settings
            # Perform search on Knowledge using the input
            # Return the search results as response
            message, errors = run_edits(settings=settings, chat=chat)
            return {
              "messages": chat.messages + [{ "role": "assistant", "content": message }],
              "errors": errors
            }

        @app.get("/api/settings")
        def settings_check(request: Request):
            logger.info("/api/settings")
            settings = request.state.settings
            check_project(settings=settings)
            global WATCH_FOLDERS
            settings.watching = True if settings.gpteng_path in WATCH_FOLDERS else False
            return {
                **settings.__dict__,
                "sub_projects": settings.sub_projects if settings.sub_projects else settings.detect_sub_projects(),
                "parent_project": settings.get_parent_project()
            }

        @app.put("/api/settings")
        async def save_settings(request: Request):
            settings = await request.json()
            GPTEngineerSettings.from_json(settings).save_project()
            
            return settings_check(request)

        @app.get("/api/project/create")
        def project_create(request: Request):
            project_path = request.query_params.get("project_path")
            if not project_path or not os.path.isdir(project_path):
                return
            settings = GPTEngineerSettings()
            settings.gpteng_path = f"{project_path}/.gpteng"
            settings.project_path = project_path
            logger.info(f"/api/project/create project_path: {project_path}")
            create_project(settings=settings)
            return settings

        @app.get("/api/profiles")
        def list_profile(request: Request):
            settings = request.state.settings
            return ProfileManager(settings=settings).list_profiles()

        @app.post("/api/profiles")
        def create_profile(profile: Profile, request: Request):
            settings = request.state.settings
            return ProfileManager(settings=settings).create_profile(profile)
            
        @app.get("/api/profiles/{profile_name}")
        def read_profile(profile_name, request: Request):
            settings = request.state.settings
            return  ProfileManager(settings=settings).read_profile(profile_name)

        @app.delete("/api/profiles/{profile_name}")
        def delete_profile(profile_name, request: Request):
            settings = request.state.settings
            ProfileManager(settings=settings).delete_profile(profile_name)
            return

        @app.get("/api/project/watch")
        def project_watch(request: Request):
            settings = request.state.settings
            global WATCH_FOLDERS
            if settings.gpteng_path not in WATCH_FOLDERS:
                WATCH_FOLDERS = WATCH_FOLDERS + [settings.gpteng_path]
            return { "OK": 1 }
        
        @app.get("/api/project/unwatch")
        def project_unwatch(request: Request):
            settings = request.state.settings
            global WATCH_FOLDERS
            if settings.gpteng_path in WATCH_FOLDERS:
                WATCH_FOLDERS = [folder for folder in WATCH_FOLDERS if folder != settings.gpteng_path]
            return { "OK": 1 }

        @app.get("/api/knowledge/keywords")
        def api_get_keywords(request: Request):
            settings = request.state.settings
            query = request.query_params.get("query")
            return get_keywords(settings=settings, query=query)

        @app.post("/api/knowledge/keywords")
        def api_extract_tags(doc: Document, request: Request):
            settings = request.state.settings
            logging.info(f"Extract keywords from {doc}")
            doc = extract_tags(settings=settings, doc=doc)
            return doc.__dict__

        return app
            
