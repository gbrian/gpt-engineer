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

from gpt_engineer.utils import extract_json_blocks 

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

from langchain.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator
class AIDocValidateResponse(BaseModel):
    analysis_example = \
    """
    In this document we can see how to access to API methods getBookings with an example:
    ```ts
      this.API.getBookings({ "from": "now", "to: "now + 10d" })
    ```
    """
    analysis_doc = \
    """
    Analyse the document and create an explanation with examples of the important parts that can help answering user's request.
    Return a simple JSON object with your response like:
    ```json
    {{
      "score": 0.8,
      "analysis": {analysis_example}
      "
    }}
    """
    score: float = Field(description="Scores how important is this document from 0 to 1")
    analysis: str = Field(description=analysis_doc)

    # You can add custom validation logic easily with Pydantic.
    @validator("score")
    def score_is_valid(cls, field):
        return field
        
def ai_validate_context(ai, dbs, prompt, doc, retry_count=0):
    assert prompt
    parser = PydanticOutputParser(pydantic_object=AIDocValidateResponse)
    validation_prompt = \
    f"""
    Given this document:
    {document_to_context(doc)}
    
    Explain how important it is for the user's request:
    >>> "{prompt}" <<<

    OUPUT INSTRUCTIONS:
    {parser.get_format_instructions()}
    ```
    Where "score" is a value from 0 to 1 indicatting how important is this document, been 1 really important.
    """
    messages = [
      HumanMessage(content=validation_prompt),
    ]
    messages = ai.next(messages=messages, step_name="ai_validate_context", max_response_length=3)
    
    response = parser.invoke(messages[-1].content.strip())
    score = response.score
    if score is None:
      if not retry_count:
        logging.error(colored(f"[validate_context] re-trying failed validation\n{prompt}\n{response}", "red"))
        return ai_validate_context(ai, dbs, prompt, doc, retry_count=1)

      logging.error(colored(f"[validate_context] failed to validate. prompt: {prompt}\nMessages: {messages}", "red"))
      score = -1
    
    doc.metadata["relevance_score"] = score
    doc.metadata["analysis"] = response.analysis
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
  logging.info(f"find_relevant_documents: Knowledge.search doc length: {len(documents)}")
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