from gpt_engineer.core.steps import document_to_context, curr_fn
from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DBs


from gpt_engineer.settings import CHAT_FILE

def chat_interaction(ai: AI, dbs: DBs):
    messages = []
    system = dbs.preprompts["roadmap"] + dbs.preprompts["philosophy"]
    print("Entering chat mode. Type your messages below (leave blank to exit):")
    while True:
        user_input = input("> ")
        if user_input == "":
            break

        # Fetch relevant documents using KnowledgeRetriever
        documents = dbs.knowledge.search(user_input)
        knwoledge_context = "\n".join([document_to_context(doc) for doc in documents])
        prompt = dbs.preprompts["chat"].format(messages="\n".join(messages), context=knwoledge_context, prompt=user_input)

        ai_messages = ai.start(system, prompt, step_name=curr_fn())
    
        response = ai_messages[-1].content.strip()
        messages.append(f"USER: {user_input}")
        messages.append(f"ASSISTANT: {response}")

    if len(messages):
      all_messages = '\n'.join(messages)
      chat_content = f"[[CHAT]]\n{all_messages}\n"
      if not dbs.project_metadata.get(CHAT_FILE):
        dbs.project_metadata[CHAT_FILE] = chat_content
      else:
        dbs.project_metadata.append(CHAT_FILE, chat_content)
    return []
