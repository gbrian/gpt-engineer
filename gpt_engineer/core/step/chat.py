import logging

from gpt_engineer.core.steps import document_to_context, parallel_validate_contexts, curr_fn
from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DBs


from gpt_engineer.settings import CHAT_FILE

def ai_chat (ai: AI, dbs: DBs, user_input: str, messages = [], system=None, role=None):
  if not system:
    system = dbs.roles[f"{role if role else 'qa'}.md"]
  else:
    logging.debug(f"[ai_chat] using custom system")
  # Fetch relevant documents using Knowledge
  documents = dbs.knowledge.search(user_input)
  documents = [doc for doc in parallel_validate_contexts(dbs, user_input, documents) if doc]

  knwoledge_context = "\n".join([document_to_context(doc) for doc in documents])
  prompt = dbs.preprompts["chat"].format(messages="\n".join(messages), context=knwoledge_context, prompt=user_input)

  ai_messages = ai.start(system, prompt, step_name=curr_fn())
  response = ai_messages[-1].content.strip()
  return response, documents 

def chat_interaction(ai: AI, dbs: DBs, user_input: str = None, messages=[]):
    print("Entering chat mode. Type your messages below (leave blank to exit):")
    role = dbs.settings.role
    while True:
        if not user_input:
          user_input = input("> ")
          if user_input == "":
              break

        # Fetch relevant documents using Knowledge
        response, documents = ai_chat(ai, dbs, user_input, messages, role=role)
        references = "\n".join([f"{doc.metadata['source']} score: {doc.metadata.get('relevance_score')}" for doc in documents])
        
        print(f"\n{response}\n\nREFERENCES\n{references}")

        messages.append(f"USER: {user_input}")
        messages.append(f"ASSISTANT: {response}")
        user_input = None

    if len(messages):
      all_messages = '\n'.join(messages)
      chat_content = f"[[CHAT]]\n{all_messages}\n"
      if not dbs.project_metadata.get(CHAT_FILE):
        dbs.project_metadata[CHAT_FILE] = chat_content
      else:
        dbs.project_metadata.append(CHAT_FILE, chat_content)
    return []
