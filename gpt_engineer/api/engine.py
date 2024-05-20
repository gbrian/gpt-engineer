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
    replace_mentions,
    notify_mentions_in_progress,
    strip_mentions
)


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
    docs, file_list = find_relevant_documents(ai=ai, dbs=dbs, query=query, settings=settings, ignore_documents=ignore_documents)
    if not docs:
        docs = []
        file_list = []

    if settings.sub_projects:
        for sub_project in settings.sub_projects.split(","):
            sub_settings = GPTEngineerSettings.from_project(f"{sub_project}/.gpteng")
            sub_docs, sub_file_list = find_relevant_documents(ai=ai, dbs=dbs, query=query, settings=sub_settings, ignore_documents=ignore_documents)
            if sub_docs:
                docs = docs + sub_docs
            if sub_file_list:
                file_list = file_list + sub_file_list
    return docs, file_list

def select_afected_files_from_knowledge(ai: AI, dbs: DBs, query: str, settings: GPTEngineerSettings):
    relevant_documents, file_list = select_afefcted_documents_from_knowledge(ai=ai, dbs=dbs, query=query, settings=settings)
    file_list = [str(Path(doc.metadata["source"]).absolute())
                  for doc in relevant_documents]
    file_list = list(dict.fromkeys(file_list))  # Remove duplicates

    return file_list


def improve_existing_code(settings: GPTEngineerSettings, chat: Chat):
    request = \
    """Create a list of files to be modified with this structure:
      <GPT_CODE_CHANGE>
      FILE: file_path
      CHANGES: Explain which changed do we need to apply to this file
      </GPT_CODE_CHANGE>
      <GPT_CODE_CHANGE>
      FILE: file_path
      CHANGES: Explain which changed do we need to apply to this file
      </GPT_CODE_CHANGE>
      Repeat for as many files we have to change
    """
    if not chat.messages[-1].improvement:
        request_chat = Chat(messages=chat.messages + [
          Message(role="user", content=request)
        ])
        request_chat = chat_with_project(settings=settings, chat=request_chat, use_knowledge=True)
        chat.messages.append(request_chat.messages[-1])
        chat.messages[-1].improvement = True
        return
    response = chat.messages[-1].content
    instructions = list(split_blocks_by_gt_lt(response))
    logging.info(f"improve_existing_code: {instructions}")
    if not instructions:
        logging.error(f"improve_existing_code ERROR no instrucctions at: {response} {chat.messages[-1]}")
    for instruction in instructions:
        file_path = instruction[0].split(":")[1].strip()
        changes = "\n".join(instruction[1:])
        logging.info(f"improve_existing_code instruction file: {file_path}")
        logging.info(f"improve_existing_code instruction changes: {changes}")
        chat.messages.append(Message(role="assistant", content="\n".join(instruction)))
        with open(file_path) as f:
          content = f.read()
        new_content = change_file(context_documents=[], query=changes, file_path=file_path, org_content=content, settings=settings)
        with open(file_path, 'w') as f:
          content = f.write(new_content)


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
    logging.info(f"check_file_for_mentions {new_files}")
    for file_path in new_files:
        try:
            check_file_for_mentions(settings=settings, file_path=file_path)
        except:
            logging.exception(f"Error checking changes in file {file_path}")

    logging.info(f"Reload knowledge files {new_files}")
    reload_knowledge(settings=settings)
    
def split_blocks_by_gt_lt(content):
    add_line = False
    content_lines = []
    for line in content.split("\n"):
      if line == "<GPT_CODE_CHANGE>":
          add_line = True
          continue
      if line == "</GPT_CODE_CHANGE>":
          yield content_lines
          add_line = False
          content_lines = []
      if add_line:
          content_lines.append(line)
          continue
          

def change_file(context_documents, query, file_path, org_content, settings):
    tasks = "\n *".join(
          context_documents + [
          query,
          "Add a line with <GPT_CODE_CHANGE> to indicate the start of the new file content",
          "Add a line with </GPT_CODE_CHANGE> to indicate the end of the new file content",
        ]
    )
    request = \
    f"""Please produce a full version of this ##CONTENT applying the changes requested in the ##TASKS section.
    The output will replace existing file so write all unchanged lines as well.
    ##CONTENT:
    {org_content}
    ##TASKS:
    {tasks}
    """
    chat = Chat(name="", 
        messages=[
            Message(role="user", content=request)
        ])
    chat = chat_with_project(settings=settings, chat=chat, use_knowledge=False)
    new_content = chat.messages[-1].content
    
    return "\n".join(next(split_blocks_by_gt_lt(new_content)))

def check_file_for_mentions(settings: GPTEngineerSettings, file_path: str):
    content = None
    with open(file_path, 'r') as f:
        content = f.read()

    def save_file (new_content):
        with open(file_path, 'w') as f:
            f.write(new_content)

    mentions = extract_mentions(content)
    new_content = notify_mentions_in_progress(content)
    save_file(new_content=new_content)
    
    if mentions:
        org_content = strip_mentions(content=content, mentions=mentions)
        try:
            def mention_info(mention):
              return f"Comment from line {mention.start_line}: {mention.mention}"

            query = "\n".join([mention_info(mention) for mention in mentions])
            context_documents = []
            if settings.use_knowledge:
              ai = build_ai(settings)
              dbs = build_dbs(settings)
              documents, _ = select_afefcted_documents_from_knowledge(ai=ai,
                                                            dbs=dbs,
                                                            query=query,
                                                            settings=settings,
                                                            ignore_documents=[f"/{file_path}"])
              if documents:
                  for doc in documents:
                      doc_context = document_to_context(doc)
                      context_documents.append(HumanMessage(content=doc_context))

            new_content = change_file(context_documents, query, file_path, org_content, settings)
        except Exception as ex:
            logging.error(str(ex), exc_info = ex)
            
        if content != new_content:
            save_file(new_content=new_content)


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
        if m.hide or m.improvement:
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
        logging.info(f"chat_with_project found {doc_length} relevant documents")
    
    file_list = chat.file_list if chat.file_list else []
    if file_list and not use_knowledge:
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