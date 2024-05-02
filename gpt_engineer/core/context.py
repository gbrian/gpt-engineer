import logging
import re
from termcolor import colored
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from gpt_engineer.core.utils import document_to_context
from gpt_engineer.core.ai import AI
from gpt_engineer.core.dbs import DBs
from gpt_engineer.core.settings import GPTEngineerSettings
from gpt_engineer.knowledge.knowledge import Knowledge

from gpt_engineer.settings import (
  PROMPT_FILE,
  HISTORY_PROMPT_FILE,
  KNOWLEDGE_MODEL
)

KNOWLEDGE_CONTEXT_SCORE_MATCH = re.compile(r".*([0-9]+)%", re.MULTILINE)

def validate_context(ai, dbs, prompt, doc, score):
    # This function now handles a single document.
    if '@ai' in doc.metadata.get('user_input', ''):
        return ai_validate_context(ai, dbs, prompt, doc)
    score = float(doc.metadata.get('user_input'))
    doc.metadata["relevance_score"] = score
    logging.debug(f"[validate_context] {doc.metadata['source']}: {score}")
    if score < score:
        return None
    return doc

def parallel_validate_contexts(dbs, prompt, documents, settings: GPTEngineerSettings):
    ai = AI(settings=settings)
    score = float(settings.knowledge_context_cutoff_relevance_score)
    if not score:
      return documents
    #dbs.input.append(
    #  HISTORY_PROMPT_FILE, f"\n[[VALIDATE_CONTEXT]]\n{prompt}\nNum docs: {len(documents)}"
    #)
    # This function uses ThreadPoolExecutor to parallelize validation of contexts.
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(ai_validate_context, ai=ai, dbs=dbs, prompt=prompt, doc=doc): doc for doc in documents}
        valid_documents = []
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                valid_documents.append(result)

        def colored_result(doc):
          res_str = f"{doc.metadata['source']}: {doc.metadata['relevance_score']}"
          if doc.metadata['relevance_score'] >= score:
            return colored(res_str, "green")
          return colored(res_str, "red")

        print("\n".join([
          "",
          colored(f"[VALIDATE WITH CONTEXT]: {prompt}", "green"),
          "\n".join([colored_result(doc) for doc in valid_documents if doc]),
          ""
        ]))
        return [doc for doc in valid_documents \
          if doc and doc.metadata.get('relevance_score', 0) >= score]
      
def get_response_score (response):
    percent = response.strip().replace("%", "")
    try:
      return float(1 / 100 * int(percent))
    except Exception as ex:
      logging.error(f"Error <{ex}> retrieving score from response: {percent} - '{response}'")
    return None
  
def ai_validate_context(ai, dbs, prompt, doc, retry_count=0):
    assert prompt
    messages = [
      HumanMessage(content=document_to_context(doc)),
      HumanMessage(content=f"Score from 0% to 100% how related is this search query with the current conversation (0% if you don't know):\n{prompt}")
    ]
    messages = ai.next(messages=messages, step_name="ai_validate_context", max_response_length=3)
    
    response = messages[-1].content.strip()
    score = get_response_score(response)
    
    if score is None:
      if not retry_count:
        logging.error(colored(f"[validate_context] re-trying failed validation\n{prompt}\n{response}", "red"))
        return ai_validate_context(ai, dbs, prompt, doc, retry_count=1)

      logging.error(colored(f"[validate_context] failed to validate. prompt: {prompt}\nMessages: {messages}", "red"))
      score = -1
    
    doc.metadata["relevance_score"] = score
    logging.debug(f"[validate_context] {doc.metadata.get('source')}: {score}")
    
    #dbs.input.append(
    #  HISTORY_PROMPT_FILE, "\n".join([
    #    str(doc.metadata),
    #    response,
    #    str(score),
    #    ""   
    #  ])
    #)
    return doc

def find_relevant_documents (ai:AI, dbs: DBs, query: str, settings, ignore_documents=[]):
  
  documents = Knowledge(settings=settings).search(query)
  def is_valid_document(doc):
    source = doc.metadata["source"]
    checks = [check for check in ignore_documents if check in source]
    if checks:
      return False
    return True
  
  documents = [doc for doc in documents if is_valid_document(doc)]
  if documents:
      # Filter out irrelevant documents based on a relevance score
      relevant_documents = [doc for doc in parallel_validate_contexts(
          dbs, query, documents, settings) if doc]
      file_list = [str(Path(doc.metadata["source"]).absolute())
                  for doc in relevant_documents]
      file_list = list(dict.fromkeys(file_list))  # Remove duplicates
      return relevant_documents, file_list
  return [], []