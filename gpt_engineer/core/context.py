import logging
import re
from termcolor import colored

from concurrent.futures import ThreadPoolExecutor, as_completed

from gpt_engineer.core.ai import AI

from gpt_engineer.settings import (
  PROMPT_FILE,
  HISTORY_PROMPT_FILE,
  KNOWLEDGE_CONTEXT_CUTOFF_RELEVANCE_SCORE,
  KNOWLEDGE_MODEL
)

KNOWLEDGE_CONTEXT_SCORE_MATCH = re.compile(r".*SCORE:\s+([0-9\.]+)", re.MULTILINE)

def validate_context(ai, dbs, prompt, doc):
    # This function now handles a single document.
    if '@ai' in doc.metadata.get('user_input', ''):
        return ai_validate_context(ai, dbs, prompt, doc)
    score = float(doc.metadata.get('user_input'))
    doc.metadata["relevance_score"] = score
    logging.debug(f"[validate_context] {doc.metadata['source']}: {score}")
    if score < KNOWLEDGE_CONTEXT_CUTOFF_RELEVANCE_SCORE:
        return None
    return doc

def parallel_validate_contexts(dbs, prompt, documents):
    ai = AI(model_name=KNOWLEDGE_MODEL)
    dbs.input.append(
      HISTORY_PROMPT_FILE, f"\n[[VALIDATE_CONTEXT]]\n{prompt}\nNum docs: {len(documents)}"
    )
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
          if doc.metadata['relevance_score'] >= KNOWLEDGE_CONTEXT_CUTOFF_RELEVANCE_SCORE:
            return colored(res_str, "green")
          return colored(res_str, "red")

        print("\n".join([
          "",
          colored(f"[VALIDATE WITH CONTEXT]: {prompt}", "green"),
          "\n".join([colored_result(doc) for doc in valid_documents if doc]),
          ""
        ]))
        return [doc for doc in valid_documents \
          if doc and doc.metadata.get('relevance_score', 0) >= KNOWLEDGE_CONTEXT_CUTOFF_RELEVANCE_SCORE]
      
def get_response_score (response):
    try:
      score_match = KNOWLEDGE_CONTEXT_SCORE_MATCH.findall(response)
      nums = score_match[0].split(".")
      score = ".".join(nums[0:2]) if len(nums) > 1 else nums[0]
      score = float(score)
      return score if score >= 0 and score <= 1 else None  
    except:
      return None
  
def ai_validate_context(ai, dbs, prompt, doc, retry_count=0):
    system = ""
    validate_prompt = dbs.preprompts["validate_context"] \
      .replace("{{ prompt }}", prompt) \
      .replace("{{ context }}", doc.page_content)

    messages = ai.start(system, validate_prompt, step_name="ai_validate_context", max_response_length=3)
    
    response = messages[-1].content.strip()
    score = get_response_score(response)
    
    if not score:
      if not retry_count:
        logging.error(colored(f"[validate_context] re-trying failed validation\n{prompt}\n{response}", "red"))
        return ai_validate_context(ai, dbs, prompt, doc, retry_count=1)

      logging.error(colored(f"[validate_context] failed to validate {prompt}\n{response}", "red"))
      score = -1
    
    doc.metadata["relevance_score"] = score
    logging.debug(f"[validate_context] {doc.metadata.get('source')}: {score}")
    
    dbs.input.append(
      HISTORY_PROMPT_FILE, "\n".join([
        str(doc.metadata),
        response,
        str(score),
        ""   
      ])
    )
    return doc