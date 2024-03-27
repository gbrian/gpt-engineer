import os
import logging
from pathlib import Path

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.schema.document import Document

from gpt_engineer.core.dbs import DBs
from gpt_engineer.core.ai import AI
from gpt_engineer.core.settings import GPTEngineerSettings
from gpt_engineer.core.utils import curr_fn, document_to_context
from gpt_engineer.tasks.task_manager import TaskManager

from gpt_engineer.api.profile_manager import ProfileManager

from gpt_engineer.api.model import Chat
from gpt_engineer.core.context import parallel_validate_contexts
from gpt_engineer.core.steps import setup_sys_prompt_existing_code
from gpt_engineer.core.chat_to_files import parse_edits, apply_edit

def create_project(settings=GPTEngineerSettings):
    logging.info(f"Create new project {settings.gpteng_path}")
    os.makedirs(settings.gpteng_path, exist_ok=True)
    settings.save_project()


def select_afefcted_documents_from_knowledge(ai: AI, dbs: DBs, query: str, settings: GPTEngineerSettings):
    documents = dbs.knowledge.search(query)
    if documents:
        # Filter out irrelevant documents based on a relevance score
        valid_documents = parallel_validate_contexts(dbs,
                                              query,
                                              documents,
                                              score=float(settings.knowledge_context_cutoff_relevance_score))
        relevant_documents = [doc for doc in valid_documents if doc]
        return relevant_documents
    return []

def select_afefcted_files_from_knowledge(ai: AI, dbs: DBs, query: str, settings: GPTEngineerSettings):
    relevant_documents = select_afefcted_documents_from_knowledge(ai=ai, dbs=dbs, query=query, settings=settings)
    file_list = [str(Path(doc.metadata["source"]).absolute())
                  for doc in relevant_documents]
    file_list = list(dict.fromkeys(file_list))  # Remove duplicates

    return file_list


def improve_existing_code(ai: AI, dbs: DBs, chat: Chat, settings: GPTEngineerSettings, profiles: [str]=["philosophy","software_developer"]):

    query = chat.messages[-1].content
    profile_manager = ProfileManager(settings=settings)
    syatem_comtent = "\n".join([profile_manager.read_profile(profile).content for profile in profiles])
    messages = [
        SystemMessage(content=syatem_comtent),
    ] + [ 
        HumanMessage(content=m.content) if m.role == "user" else AIMessage(content=m.content) \
          for m in chat.messages[:-1] if not hasattr(m, "hide")
    ]

    relevant_documents = select_afefcted_documents_from_knowledge(ai=ai,
                                                        dbs=dbs,
                                                        query=query,
                                                        settings=settings)
    for doc in relevant_documents:
        doc_context = document_to_context(doc)
        messages.append(HumanMessage(content=doc_context))

    messages.append(HumanMessage(content=query))
    messages = ai.next(messages, step_name=curr_fn())

    response = messages[-1].content
    edits = []
    try:
      edits = parse_edits(response)
    except:
      pass
    affected_files = dict.fromkeys([edit.filename for edit in edits])

    errors = []
    try:
      for edit in edits:
        success, error = apply_edit(edit=edit, workspace=dbs.workspace)
        if error:
          errors.append(error)
    except Exception as ex:
      errors.append(str(ex))

    return (messages, edits, errors, affected_files)

def check_knowledge_status(dbs: DBs):
    logging.info("check_knowledge_status")
    loader = dbs.knowledge.loader
    last_update = dbs.knowledge.last_update
    status = dbs.knowledge.status()
    all_sources = dbs.knowledge.get_all_sources()
    pending_files = loader.list_repository_files(
                        last_update=last_update if all_sources else None,
                        current_sources=all_sources)
    return {
      "last_update": str(last_update),
      "pending_files": pending_files,
      **status
    }

def run_edits(ai: AI, dbs: DBs, chat: Chat):
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

def get_chat(settings: GPTEngineerSettings):
    pass
