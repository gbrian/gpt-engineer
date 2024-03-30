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

from gpt_engineer.api.model import Chat, Message
from gpt_engineer.core.context import parallel_validate_contexts
from gpt_engineer.core.steps import setup_sys_prompt_existing_code
from gpt_engineer.core.chat_to_files import parse_edits, apply_edit

from gpt_engineer.core.mention_manager import extract_mentions

FILE_WATCH_MANGER = None

def reload_knowledge(settings: GPTEngineerSettings):
    ai = build_ai(settings=settings)
    dbs = build_dbs(settings=settings, ai=ai)
    dbs.reload()

def on_project_changed(project_path: str, file_path: str):
    logging.info(f"Project changed {project_path} - {file_path}")

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
                                              settings=settings)
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
    last_update = dbs.knowledge.last_update
    status = dbs.knowledge.status()
    pending_files = dbs.knowledge.detect_changes()
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

def check_project_changes(settings: GPTEngineerSettings):
    dbs = build_dbs(settings=settings)
    dbs.knowledge.clean_deleted_documents()
    new_files = dbs.knowledge.detect_changes()
    if not new_files:
        return
    logging.info(f"Reload knowledge files {new_files}")
    dbs.knowledge.reload()
    for file_path in new_files:
        check_file_for_mentions(settings=settings, file_path=file_path)    

def check_file_for_mentions(settings: GPTEngineerSettings, file_path: str):
    with open(file_path, 'r') as f:
        content = f.read()
        mentions = extract_mentions(content)
        if mentions:
            process_file_mentions(settings=settings, file_path=file_path, mentions=mentions)        

def process_file_mentions(settings: GPTEngineerSettings, file_path, mentions):
    logging.info(f"File with mentions {file_path}: {mentions}")


def chat_with_project(settings: GPTEngineerSettings, chat: Chat):
    ai = build_ai(settings)
    dbs = build_dbs(settings, ai=ai)
    
    # Perform search on Knowledge using the input
    # Return the search results as response
    user_input = chat.messages[-1].content
    messages = [m.content for m in chat.messages[:-1] if not hasattr(m, "hide")]
    philosophy = ProfileManager(settings=settings).read_profile("philosophy").content
    messages = [philosophy] + messages
    response, documents = ai_chat(ai=ai, dbs=dbs, user_input=user_input, messages=messages, settings=settings)
    if documents:
        doc_content = '\n'.join([document_to_context(doc) for doc in documents])
        response = f"{response}\n{doc_content}"
    response_message = Message(role="assistant", hidden=False, content=response, documents=documents)
    chat.messages.append(response_message)
    return chat
