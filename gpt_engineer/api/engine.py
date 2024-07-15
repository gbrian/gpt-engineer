import os
import logging
import re
import json
from pathlib import Path
from datetime import datetime

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.schema.document import Document

from gpt_engineer.utils import extract_code_blocks, extract_json_blocks 

from gpt_engineer.core.dbs import DBs
from gpt_engineer.core.ai import AI
from gpt_engineer.core.settings import GPTEngineerSettings
from gpt_engineer.core import build_dbs, build_ai
from gpt_engineer.core.utils import curr_fn, document_to_context
from gpt_engineer.core.step.chat import ai_chat

from gpt_engineer.core.chat_manager import ChatManager
from gpt_engineer.tasks.task_manager import TaskManager

from gpt_engineer.api.profile_manager import ProfileManager

from gpt_engineer.api.model import (
    Chat,
    Message,
    KnowledgeSearch,
    Document
)
from gpt_engineer.core.context import find_relevant_documents, AI_CODE_VALIDATE_RESPONSE_PARSER
from gpt_engineer.core.steps import setup_sys_prompt_existing_code
from gpt_engineer.core.chat_to_files import parse_edits, apply_edit

from gpt_engineer.knowledge.knowledge import Knowledge
from gpt_engineer.knowledge.knowledge_loader import KnowledgeLoader
from gpt_engineer.knowledge.knowledge_keywords import KnowledgeKeywords

from gpt_engineer.core.mention_manager import (
    extract_mentions,
    replace_mentions,
    notify_mentions_in_progress,
    notify_mentions_error,
    strip_mentions
)

logger = logging.getLogger(__name__)

def reload_knowledge(settings: GPTEngineerSettings, path: str = None):
    knowledge = Knowledge(settings=settings)
    logger.info(f"***** reload_knowledge: {path}")
    if path:
        documents = knowledge.reload_path(path)
        logger.info(f"reload_knowledge: {path} - Docs: {len(documents)}")
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
    def process_rag_query(rag_query):
        docs, file_list = find_relevant_documents(ai=ai, dbs=dbs, query=rag_query, settings=settings, ignore_documents=ignore_documents)
        if not docs:
            docs = []
            file_list = []
        logging.info(f"select_afefcted_documents_from_knowledge doc length: {len(docs)}")
        if hasattr(settings, "sub_projects") and settings.sub_projects:
            for sub_project in settings.get_sub_projects():
                sub_settings = GPTEngineerSettings.from_project(f"{sub_project}/.gpteng")
                sub_docs, sub_file_list = find_relevant_documents(ai=ai, dbs=dbs, query=rag_query, settings=sub_settings, ignore_documents=ignore_documents)
                if sub_docs:
                    docs = docs + sub_docs
                if sub_file_list:
                    file_list = file_list + sub_file_list
        return docs, file_list
    # Temp disable multiple rag_query
    return process_rag_query(rag_query=query)

    rag_queries = "\n".join([
        "Extract up to 3 search queries from the user request.",
        "Each search query will be used to search relevant documents to enrich user's request.",
        "It's important to be able able to find relevant documents to enrich user's request.",
        "Return only the queries one by one on their on line",
        "QUERY:",
        query
    ])
    query_messages = ai.next(messages=[HumanMessage(content=rag_queries, role="user")], step_name="select_afefcted_documents_from_knowledge_split_query")
    response = query_messages[-1].content
    logging.info(f"select_afefcted_documents_from_knowledge RAG queries: {response}")
    all_docs = {}
    for rag_query in [query for query in response.split("\n") if query]:
        docs, _ = process_rag_query(rag_query)
        if docs:
            for doc in docs:
                key = f"{doc.metadata['source']}-{doc.metadata.get('index') or 0}"
                all_docs[key] = doc
    all_docs = [doc for doc in all_docs.values()]
    all_files = list(set(([doc.metadata["source"] for doc in all_docs])))
    return all_docs, all_files 
      

def select_afected_files_from_knowledge(ai: AI, dbs: DBs, query: str, settings: GPTEngineerSettings):
    relevant_documents, file_list = select_afefcted_documents_from_knowledge(ai=ai, dbs=dbs, query=query, settings=settings)
    file_list = [str(Path(doc.metadata["source"]).absolute())
                  for doc in relevant_documents]
    file_list = list(dict.fromkeys(file_list))  # Remove duplicates

    return file_list


def improve_existing_code(settings: GPTEngineerSettings, chat: Chat):
    request = \
    """Create a list of fin&replace intructions for each change needed:

      ```JSON
      [
        {
          "change": {
            "type": "update",
            "file": "/file/path/to/file,
            "existingContent": "def myFunction(self):",
            "newContent": "def myFunction(self, chat: Chat = None):",
          }
        },
        {
          "change": {
            "type": "new",
            "file": "/file/path/to/file,
            "existingContent": null,
            "newContent": "class MyClass:\n       def __init__(self):\n         pass",
          }
        },
        {
          "change": {
            "type": "delete",
            "file": "/file/path/to/file,
            "existingContent": null,
            "newContent": null,
          }
        }
      ]
      ```

      INSTRUCTIONS:
        * change structure:
          - type: str. It can be "update", "delete" or "new"
          - file: str. Absolute file path for the file to be changed
          - existingContent: str. Anchor point in the existing content to start replacing with new code. New code will include it if anchor point still needed or not to replce it.
          - newContent: str. New copntent to update "existingContent" or empty to remove "existingContent"
        * Create one entry for each change
        * Keep content identation; is crucial to find the content to replace and to make new content work
    """
    if not chat.messages[-1].improvement:
        chat.messages.append(Message(role="user", content=request))
        chat = chat_with_project(settings=settings, chat=chat, use_knowledge=False)
        chat.messages = [msg for msg in chat.messages if msg.content != request]
        chat.messages[-1].improvement = True
        return
    
    response = chat.messages[-1].content
    apply_improve_code_changes(response=response)

def apply_improve_code_changes(response: str):
    changes = list(extract_changes(response))
    logging.info(f"improve_existing_code total changes: {len(changes)}")
    for change in changes:
      logging.info(f"improve_existing_code change: {change}")
      if change["type"] == "update":
          file_path = change["file"]
          existing_content = change["existingContent"]
          new_content = change["newContent"]
          with open(file_path, 'r') as f:
              content = f.read()
              new_content = content.replace(existing_content, new_content)
          with open(file_path, 'w') as f:
              f.write(new_content)
    

def improve_existing_code_gpt_blocks(settings: GPTEngineerSettings, chat: Chat):
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
    ChatManager(settings=settings).save_chat(chat)

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

def extract_changes(content):
    for block in extract_json_blocks(content):
        try:
            for change in block:
                yield change["change"]
        except:
            pass

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

def get_line_changes(content):
    line_change = None
    for line in content.split("\n"):
      if line.startswith("<GPT_"):
          line_change = {
            "type": re.match(r'<GPT_([^_]+)_LINE', line),
            "start": line.split("start_line=")[1]
          }
          continue
      if line.startswith("</GPT"):
          yield content_lines
          add_line = False
          content_lines = []
      if add_line:
          content_lines.append(line)
          continue
          
def change_file_by_blocks(context_documents, query, file_path, org_content, settings, save_changes=False, profile=None):
    profile_manager = ProfileManager(settings=settings)
    tasks = "\n *".join(
            context_documents + [
            query,
            'To ADD line(s) use: <GPT_ADD_LINE start_line="10"></GPT_ADD_LINE>',
            'To REMOVE line(s) use: <GPT_REMOVE_LINE start_line="10" end_line="11"></GPT_ADD_LINE> Lines from 10 to 11 will be deleted, both included',
            'To CHANGE line(s) use: <GPT_CHANGE_LINE start_line="10" end_line="11">New content</GPT_ADD_LINE> New content will replace lines 10 to 11',
            'Make sure identantion for new content is consistent'
          ]
    )
    request = \
    f"""Given this CONTENT, generate line changes.
    ##CONTENT:
    {org_content}
    ##TASKS:
    {tasks}
    """

    chat_name = '-'.join(file_path.split('/')[-2:])
    chat_time = datetime.now().strftime('%H%M%S')
    chat = Chat(name=f"{chat_name}_{chat_time}", 
        messages=[
            Message(role="user", content=request)
        ])
    try:
        if profile:
            profile_content = profile_manager.read_profile(profile).content
            if profile_content:
                chat.messages = [
                  Message(role="system", content=profile_content),
                ] + chat.messages

        chat = chat_with_project(settings=settings, chat=chat, use_knowledge=False)
        new_content = chat.messages[-1].content
        
        return "\n".join(next(split_blocks_by_gt_lt(new_content)))
    except Exception as ex:
        chat.messages.append(Message(role="error", content=str(ex)))
        raise ex
    finally:
        if save_changes:
            save_chat(chat=chat, settings=settings)

def change_file(context_documents, query, file_path, org_content, settings, save_changes=False):
    profile_manager = ProfileManager(settings=settings)
    tasks = "\n *".join(
            context_documents + [
            query
          ]
    )
    request = f"""Please produce a full version of this ##CONTENT applying the changes requested in the ##TASKS section.
    The output will replace existing file so write all unchanged lines as well.
    ##CONTENT:
    {org_content}
    
    ##TASKS:
    {tasks}

    OUPUT INSTRUCTIONS:
    {AI_CODE_VALIDATE_RESPONSE_PARSER.get_format_instructions()}
    """

    chat_name = '-'.join(file_path.split('/')[-2:])
    chat_time = datetime.now().strftime('%H%M%S')
    chat = Chat(name=f"{chat_name}_{chat_time}", 
        messages=[
            Message(role="user", content=request)
        ])
    try:
        chat = chat_with_project(settings=settings, chat=chat, use_knowledge=False)
        response = chat.messages[-1].content.strip()
        parsed_response = AI_CODE_VALIDATE_RESPONSE_PARSER.invoke(response)
        return parsed_response.new_content
    except Exception as ex:
        chat.messages.append(Message(role="error", content=str(ex)))
        raise ex
    finally:
        if save_changes:
            save_chat(chat=chat, settings=settings)


def check_file_for_mentions(settings: GPTEngineerSettings, file_path: str):
    content = None
    with open(file_path, 'r') as f:
        content = f.read()

    def save_file (new_content):
        with open(file_path, 'w') as f:
            f.write(new_content)

    mentions = extract_mentions(content)
    if not mentions:
        return
    new_content = notify_mentions_in_progress(content)
    save_file(new_content=new_content)
    
    if mentions:
        org_content = strip_mentions(content=content, mentions=mentions)
        try:
            def mention_info(mention):
              return f"Comment from line {mention.start_line}: {mention.mention}"

            query = "\n".join([mention_info(mention) for mention in mentions])
            
            
            context_documents = []
            use_knowledge = False if "--codx-no-knowledge" in query else True
            if use_knowledge:
              query = query.replace("--codx-knowledge", "")
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
                      context_documents.append(doc_context)

            save_changes = True if "--codx-save" in query else False
            new_content = change_file(
                context_documents=context_documents,
                query=query,
                file_path=file_path,
                org_content=org_content,
                settings=settings,
                save_changes=save_changes)
        except Exception as ex:
            new_content = notify_mentions_error(content=content, error=str(ex))
            logging.exception(f"Error {ex} processig mention {query}")
            
            
        if content != new_content:
            save_file(new_content=new_content)


def chat_with_project(settings: GPTEngineerSettings, chat: Chat, use_knowledge: bool=True, callback=None):
    ai = build_ai(settings)
    dbs = build_dbs(settings)
    profile_manager = ProfileManager(settings=settings)

    messages = [
      HumanMessage(content=profile_manager.read_profile("project").content)
    ]
    query = chat.messages[-1].content
    for m in chat.messages[0:-1]:
        if m.hide or m.improvement:
            continue
        msg = HumanMessage(content=m.content) if m.role == "user" else AIMessage(content=m.content)
        messages.append(msg)

    context = ""
    documents = []
    if use_knowledge:
        affected_documents, doc_file_list = select_afefcted_documents_from_knowledge(ai=ai,
                                                        dbs=dbs,
                                                        query=query,
                                                        settings=settings,
                                                        ignore_documents=[f"/{chat.name}"])
        if affected_documents:
            documents = affected_documents
            file_list = doc_file_list
            documents = affected_documents
            for doc in documents:
                doc_context = document_to_context(doc)
                context = context + f"{doc_context}\n"
        doc_length = len(documents) if documents else 0
        logging.info(f"chat_with_project found {doc_length} relevant documents")

    
    messages.append(AIMessage(content=f"THIS INFORMATION IS COMING FROM PROJECT'S FILES. HOPE IT HELPS TO ANSWER USER REQUEST.\n\n{context}"))
    messages.append(HumanMessage(content=f"{query}\n\nPlease when using references to methods or classes tell me the class and file where they are"))
    messages = ai.next(messages, step_name=curr_fn(), callback=callback)
    response = messages[-1].content
    if documents:
        sources = list(set([f" * {doc.metadata['source']}" for doc in documents]))
        sources = '\n'.join([f' * {source}' for source in sources])
        response = f"{messages[-1].content}\n\nRESOURCES:\n\n{sources}"

    response_message = Message(role="assistant", content=response)
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

def find_all_projects():
    all_projects = []
    project_paths = os.environ.get("PROJECT_PATHS", "").split(" ")
    logger.info(f"find_projects_to_watch: Scanning project paths: {project_paths}")
    for project_path in project_paths:
        for project_settings in Path(project_path).glob("**/.gpteng"):
            logger.info(f"find_projects_to_watch: project found {str(project_settings)}")
            try:
                settings = GPTEngineerSettings.from_project(gpteng_path=str(project_settings))
                if settings.gpteng_path not in all_projects:
                    all_projects = all_projects + [settings]
            except Exception as ex:
                logger.exception(f"Error loading project {str(project_settings)}")
    return all_projects
