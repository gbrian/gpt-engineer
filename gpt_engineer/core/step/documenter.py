import logging

from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DBs
from gpt_engineer.core.steps import curr_fn
from gpt_engineer.core.chat_to_files import parse_edits


def create_project_summary(ai: AI, dbs: DBs):
    system = dbs.roles["documenter.md"]
    template = dbs.preprompts["project_summary"]
    summary = dbs.project_metadata.get("summary.md", "")
    

    documents = dbs.knowledge.get_all_documents(include=['documents'])
    logging.info(f"[create_project_summary] document count {len(documents)}")
    
    for doc in documents:
      source = doc.metadata["source"]
      language = doc.metadata["language"]
      content = doc.page_content

      logging.debug(f"Updating summary {source} {language}")
      
      prompt = template.replace("{{ SOURCE }}", source) \
                        .replace("{{ LANGUAGE }}", language) \
                        .replace("{{ CONTENT }}", content) \
                        .replace("{{ SUMMARY }}", summary)

      # print(f"[Summarizing]\n{prompt}")

      messages = ai.start(system, prompt, step_name=curr_fn()) 
      response = messages[-1].content.strip()
      if [l for l in response.split("\n") if "<NO CHANGES>" in l]:
        continue
      edits = parse_edits(response)
      # print(f"\n\n{prompt}\n***********************\n{response}\n\n{edits}")
      
      for edit in edits:
        summary = summary.replace(edit.before, edit.after)
      dbs.project_metadata["summary.md"] = summary
    return []
