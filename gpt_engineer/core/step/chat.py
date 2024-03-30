import logging
from datetime import datetime

from gpt_engineer.core.utils import curr_fn, document_to_context
from gpt_engineer.core.ai import AI
from gpt_engineer.core.dbs import DBs
from gpt_engineer.core.context import find_relevant_documents


from gpt_engineer.settings import (
  HISTORY_PROMPT_FILE,
  CHAT_FILE
)

def ai_chat (ai: AI, dbs: DBs, user_input: str, settings, messages = [], system=None, role=None, ignore_documents=[]):
  if not system:
      system = dbs.roles[f"{role if role else 'qa'}.md"]
  else:
      logging.debug(f"[ai_chat] using custom system")
  # Fetch relevant documents using Knowledge
  documents, file_list = find_relevant_documents(
      ai, dbs, query=user_input, settings=settings, ignore_documents=ignore_documents)

  knwoledge_context = "\n".join([document_to_context(doc) for doc in documents]) \
                        if documents else ""
  prompt = dbs.preprompts["chat"].format(messages="\n".join(messages), context=knwoledge_context, prompt=user_input)

  ai_messages = ai.start(system, prompt, step_name=curr_fn())
  response = ai_messages[-1].content.strip()
  return response, documents 

def chat_interaction(ai: AI, dbs: DBs, user_input: str = None, messages=[]):
    print("Entering chat mode. Type your messages below (leave blank to exit):")
    role = dbs.settings.role
    dbs.input.append(
      HISTORY_PROMPT_FILE, f"\n[[CHAT]]\n{datetime.now()}\n"
    )
    
    while True:
        if not user_input:
          user_input = input("> ")
          if user_input == "":
              break
        # Fetch relevant documents using Knowledge
        response, documents = ai_chat(ai, dbs, user_input, messages, role=role)
        references = "\n".join([f"{doc.metadata['source']} score: {doc.metadata.get('relevance_score')}" for doc in documents])
        dbs.input.append(
          HISTORY_PROMPT_FILE, "\n".join([
            f"Q: {user_input}",
            f"A: {response}",
            references
          ])
        )

        print(f"\n{response}\n\nREFERENCES\n{references}")

        messages.append(f"USER: {user_input}")
        messages.append(f"ASSISTANT: {response}")
        user_input = None

    return []
