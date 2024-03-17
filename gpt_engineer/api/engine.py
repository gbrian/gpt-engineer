from pathlib import Path

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.schema.document import Document

from gpt_engineer.core.dbs import DBs
from gpt_engineer.core.ai import AI
from gpt_engineer.core.utils import curr_fn, document_to_context

from gpt_engineer.api.model import ChatMessage
from gpt_engineer.core.context import parallel_validate_contexts
from gpt_engineer.core.steps import setup_sys_prompt_existing_code
from gpt_engineer.core.chat_to_files import parse_edits, apply_edits

def select_afefcted_files_from_knowledge(ai: AI, dbs: DBs, query: str):
    documents = dbs.knowledge.search(query)
    if documents:
        # Filter out irrelevant documents based on a relevance score
        relevant_documents = [doc for doc in parallel_validate_contexts(
            dbs, query, documents) if doc]
        file_list = [str(Path(doc.metadata["source"]).absolute())
                     for doc in relevant_documents]
        file_list = list(dict.fromkeys(file_list))  # Remove duplicates

        return file_list
    return []


def improve_existing_code(ai: AI, dbs: DBs, chat_message: ChatMessage):

    query = chat_message.messages[-1].content
    messages = [
        SystemMessage(content=setup_sys_prompt_existing_code(dbs)),
    ] + [ 
        HumanMessage(content=m.content) if m.role == "user" else AIMessage(content=m.content) \
          for m in chat_message.messages[:-1] 
    ]

    for file_path in select_afefcted_files_from_knowledge(ai=ai, dbs=dbs, query=query):
        with open(file_path, 'r') as f:
            doc = Document(
              page_content=f.read(),
              metadata={
                "source": file_path,
                "laguage": file_path.split(".")[-1] if "." in file_path else ""
              })
            messages.append(HumanMessage(content=document_to_context(doc)))

    messages.append(HumanMessage(content=query))
    messages = ai.next(messages, step_name=curr_fn())

    response = messages[-1].content
    edits = parse_edits(response)

    error = None
    try:
      apply_edits(chat=response, dbs=dbs, no_wait=True)
    except Exception as ex:
      error = ex
    return (messages, edits, error)

def check_knowledge_status(dbs: DBs):
    loader = dbs.knowledge.loader
    last_update = dbs.knowledge.last_update
    pending_files = loader.list_repository_files(last_update)
    return {
      "last_update": str(last_update),
      "pending_files": pending_files
    }