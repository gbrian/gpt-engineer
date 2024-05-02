import os
import logging
from pathlib import Path

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.schema.document import Document

from gpt_engineer.core.dbs import DBs
from gpt_engineer.core.ai import AI
from gpt_engineer.core.settings import GPTEngineerSettings
from gpt_engineer.core import build_dbs, build_ai
from gpt_engineer.core.utils import curr_fn, document_to_context
from gpt_engineer.core.step.chat import ai_chat

from gpt_engineer.tasks.task_manager import TaskManager

from gpt_engineer.api.profile_manager import ProfileManager

from gpt_engineer.api.model import (
    Chat,
    Message,
    KnowledgeSearch,
    Document
)
from gpt_engineer.core.context import find_relevant_documents
from gpt_engineer.core.steps import setup_sys_prompt_existing_code
from gpt_engineer.core.chat_to_files import parse_edits, apply_edit

from gpt_engineer.knowledge.knowledge import Knowledge
from gpt_engineer.knowledge.knowledge_loader import KnowledgeLoader
from gpt_engineer.knowledge.knowledge_keywords import KnowledgeKeywords

from gpt_engineer.core.mention_manager import (
    extract_mentions,
    replace_mentions
)


FILE_WATCH_MANGER = None

def reload_knowledge(settings: GPTEngineerSettings, path: str = None):
    knowledge = Knowledge(settings=settings)
    if path:
        documents = knowledge.reload_path(path)
        return { "doc_count": len(documents) if documents else 0 }
    
    knowledge.reload()

def knowledge_search(settings: GPTEngineerSettings, knowledge_search: KnowledgeSearch):
    if knowledge_search.document_search_type:
        settings.knowledge_search_type = knowledge_search.document_search_type
    if knowledge_search.document_count:
        settings.knowledge_search_document_count = knowledge_search.document_count
    if knowledge_search.document_cutoff_score:
        settings.knowledge_context_cutoff_relevance_score = knowledge_search.document_cutoff_score
    
    dbs = build_dbs(settings=settings)
    ai = build_ai(settings=settings)
    documents = []
    if knowledge_search.search_type == "embeddings":
        documents, _ = select_afefcted_documents_from_knowledge(ai=ai, dbs=dbs, query=knowledge_search.search_term, settings=settings)
    if knowledge_search.search_type == "source":
        documents = Knowledge(settings=settings).search_in_source(knowledge_search.search_term)
    return { 
        "documents": documents, 
        "settings": {
            "knowledge_search_type": settings.knowledge_search_type,
            "knowledge_search_document_count": settings.knowledge_search_document_count,
            "knowledge_context_cutoff_relevance_score": settings.knowledge_context_cutoff_relevance_score 
        }
    }

def delete_knowledge_source(settings: GPTEngineerSettings, sources: [str]):
    Knowledge(settings=settings).delete_documents(sources=sources)
    return { "ok": 1 }

def on_project_changed(project_path: str, file_path: str):
    logging.info(f"Project changed {project_path} - {file_path}")

def create_project(settings=GPTEngineerSettings):
    logging.info(f"Create new project {settings.gpteng_path}")
    os.makedirs(settings.gpteng_path, exist_ok=True)
    settings.save_project()


def select_afefcted_documents_from_knowledge(ai: AI, dbs: DBs, query: str, settings: GPTEngineerSettings, ignore_documents=[]):
    return find_relevant_documents(ai=ai, dbs=dbs, query=query, settings=settings, ignore_documents=ignore_documents)

def select_afected_files_from_knowledge(ai: AI, dbs: DBs, query: str, settings: GPTEngineerSettings):
    relevant_documents, file_list = select_afefcted_documents_from_knowledge(ai=ai, dbs=dbs, query=query, settings=settings)
    file_list = [str(Path(doc.metadata["source"]).absolute())
                  for doc in relevant_documents]
    file_list = list(dict.fromkeys(file_list))  # Remove duplicates

    return file_list


def improve_existing_code(settings: GPTEngineerSettings, chat: Chat):
    dbs = build_dbs(settings=settings)
    ai = build_ai(settings=settings)
    
    chat = chat_with_project(settings=settings, chat=chat, use_knowledge=False)

    response = chat.messages[-1].content

    edits = []
    try:
      edits = parse_edits(response)
    except:
      pass
    affected_files = []

    errors = []
    try:
      for edit in edits:
        success, error = apply_edit(edit=edit, workspace=dbs.workspace)
        if error:
          errors.append(error)
    except Exception as ex:
      errors.append(str(ex))

    return (chat.messages, edits, errors, affected_files)

def check_knowledge_status(settings: GPTEngineerSettings):
    knowledge = Knowledge(settings=settings)
    last_update = knowledge.last_update
    status = knowledge.status()
    pending_files = knowledge.detect_changes()
    return {
      "last_update": str(last_update),
      "pending_files": pending_files,
      **status
    }

def run_edits(settings: GPTEngineerSettings, chat: Chat):
    dbs = build_dbs(settings=settings)
    ai = build_ai(settings=settings)
    
    errors = []
    total_edits = []
    for message in chat.messages:
      if hasattr(message, "hide"):
        continue
      try:
        edits = parse_edits(message.content)
        total_edits = total_edits + edits
        for edit in edits:
          success, error = apply_edit(edit=edit, workspace=dbs.workspace)
          errors.append(f"{edit.filename} error: {error}")
      except Exception as ex:
        errors.append(str(ex))
    return f"{len(total_edits)} edits, {len(errors)} errors", errors

def save_chat(chat: Chat, settings: GPTEngineerSettings):
    task_manager = TaskManager(settings)
    task_id = len(task_manager.get_all_tasks()) + 1
    task_manager.create_task(task_id, chat)

def check_project_changes(settings: GPTEngineerSettings):
    knowledge = Knowledge(settings=settings)
    knowledge.clean_deleted_documents()
    new_files = knowledge.detect_changes()
    
    if not new_files:
        return
    logging.info(f"Reload knowledge files {new_files}")
    knowledge.reload()
    for file_path in new_files:
        check_file_for_mentions(settings=settings, file_path=file_path)    

def check_file_for_mentions(settings: GPTEngineerSettings, file_path: str):
    content = None
    with open(file_path, 'r') as f:
        content = f.read()

    mentions = extract_mentions(content)
    if mentions:
        for mention in mentions:
            try:
                chat = Chat(name="", 
                  messages=[
                      Message(role="user", content=content),
                      Message(role="user", content=mention.mention)
                  ])
                chat = chat_with_project(settings=settings, chat=chat)
                mention.respone = chat.messages[-1].content
            except Exception as ex:
                logging.error(str(ex), exc_info = ex)
                mention.respone = f"{mention.mention}/nError: str({ex})"
        new_content = replace_mentions(content=content, mentions=mentions)
        if content != new_content:
            with open(file_path, 'w') as f:
                f.write(new_content)


def chat_with_project(settings: GPTEngineerSettings, chat: Chat, use_knowledge: bool=True, callback=None):
    ai = build_ai(settings)
    dbs = build_dbs(settings)
    
    query = chat.messages[-1].content
    profile_manager = ProfileManager(settings=settings)
    profiles = list(set(["gpt-engineer", "project"] + chat.profiles))
    system_content = "\n".join([profile_manager.read_profile(profile).content for profile in profiles])
    
    messages = []
    if system_content:
        messages.append(SystemMessage(content=system_content))
    
    for m in chat.messages[0:-1]:
        if hasattr(m, "hide") and m.hide:
            continue
        msg = HumanMessage(content=m.content) if m.role == "user" else AIMessage(content=m.content)
        messages.append(msg)

    documents = []
    file_list = []
    if use_knowledge:
        documents, file_list = select_afefcted_documents_from_knowledge(ai=ai,
                                                        dbs=dbs,
                                                        query=query,
                                                        settings=settings,
                                                        ignore_documents=[f"/{chat.name}"])
        if documents:
            for doc in documents:
                doc_context = document_to_context(doc)
                messages.append(HumanMessage(content=doc_context))
        doc_length = len(documents) if documents else 0
        logging.info(f"chat_with_project found {doc_length} relevan documents")
    
    file_list = chat.file_list if chat.file_list else []
    if file_list:
        for doc in Knowledge.get_documents_from_sources(file_list):
            doc_context = document_to_context(doc)
            messages.append(HumanMessage(content=doc_context))

    messages.append(HumanMessage(content=query))
    messages = ai.next(messages, step_name=curr_fn(), callback=callback)
    response = messages[-1].content
    
    if documents:
        doc_file_list = [doc.metadata["source"] for doc in documents]
        chat.file_list = list(set(file_list + doc_file_list))
        logging.info(f"chat_with_project file_list: {chat.file_list}")
    
    response_message = Message(role="assistant", hidden=False, content=response, documents=documents)
    chat.messages.append(response_message)
    return chat

def check_project(settings: GPTEngineerSettings):
    try:
        logging.info(f"check_project")
        loader = KnowledgeLoader(settings=settings)
        loader.fix_repo()
    except Exception as ex:
        logging.exception(str(ex))

def extract_tags(settings: GPTEngineerSettings, doc):
    knowledge = Knowledge(settings=settings)
    knowledge.extract_doc_keywords(doc)
    return doc

def get_keywords(settings: GPTEngineerSettings, query):
    return KnowledgeKeywords(settings=settings).get_keywords(query)