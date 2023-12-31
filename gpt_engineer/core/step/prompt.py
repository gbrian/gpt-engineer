import logging
from termcolor import colored

from gpt_engineer.core.steps import document_to_context, curr_fn, validate_context
from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DBs

from gpt_engineer.core.step.chat import ai_chat

from gpt_engineer.settings import (
  PROMPT_FILE,
  HISTORY_PROMPT_FILE,
  PROJECT_SUMMARY,
  LANGUAGE_FROM_EXTENSION,
)

MORE_INFO_IS_NEEDED="MORE INFO IS NEEDED:"
USER_FEEDBACK="USER FEEDBACK:"

def get_prompt (ai: AI, dbs: DBs):
    curr_prompt = dbs.input.get(PROMPT_FILE)
    input_text = "Write new prompt or Enter to continue:\n"
    if curr_prompt:
      print(f"Current prompt at <{PROMPT_FILE}>:")
      print(
        colored(
            f"{curr_prompt}",
            "green",
          )
        )
      input_text = "\nChange prompt or leave it blank to continue:\n"
      
    new_prompt = input(input_text)
    
    if new_prompt:
      dbs.input[PROMPT_FILE] = new_prompt
      return new_prompt
  
    if not new_prompt and curr_prompt:
      return curr_prompt

    raise "We need a prompt to start"

def improve_prompt_with_summary(ai:AI, dbs: DBs):
    logging.debug(f"Improving prompt with summary")
    template = dbs.preprompts["enrich_prompt"]
    prompt = dbs.input[PROMPT_FILE]
    context = dbs.project_metadata.get(PROJECT_SUMMARY) if PROJECT_SUMMARY else ""

    improve_prompt = template.replace("{{ TASK }}", prompt).replace("{{ CONTEXT }}", context)
    
    dbs.input.append(
        HISTORY_PROMPT_FILE, f"\n[[PROPMT_IMPROVEMNET]]\n{improve_prompt}"
    )
    system = dbs.preprompts["roadmap"] + dbs.preprompts["philosophy"]
    messages = ai.start(system, improve_prompt, step_name=curr_fn())
    
    new_prompt = messages[-1].content.strip()
    new_prompt = solve_prompt_questions(ai, dbs, new_prompt)
    dbs.input[PROMPT_FILE] = new_prompt

def solve_prompt_questions(ai:AI, dbs: DBs, prompt: str):
    if not MORE_INFO_IS_NEEDED in prompt:
      return prompt

    def is_q(question):
      question = question.strip()
      if len(question):
        return True if question[0] == '-' else False
      return False
  
    logging.debug(f"Solving prompt questions")
    more_info_needed = prompt.split(MORE_INFO_IS_NEEDED)[1]
    questions = [question for question in more_info_needed.split("\n") if is_q(question)]
    logging.debug(f"More info found: {more_info_needed}")
    logging.debug(f"Questions: {questions}")
    for question in questions:
      question_request = [
        "*** QUESTION *******************************************",
        f"{question}",
        "********************************************************",
        "Write @AI to ask AI to answer that question",
        "write your own answer",
        "Leave blank to remove the question",
        ": "
      ]
      print()
      opt = input("\n".join(question_request))
      logging.debug(f"User response: {opt}")
      response = opt
      if opt.lower() == '@ai':
        response = ai_chat(ai, dbs, question, messages=[prompt])
      if not response:
        prompt = prompt.replace(question, "")
      else:
        prompt = prompt.replace(question, f"Q: {question}\nA: {response}\n")
    prompt = prompt.replace(MORE_INFO_IS_NEEDED, USER_FEEDBACK)
    return prompt

def improve_prompt_with_knowledge(ai:AI, dbs: DBs):
    template = dbs.preprompts["enrich_prompt"]
    prompt = dbs.input[PROMPT_FILE]
    knowledge_docs = [validate_context(ai, dbs, prompt, doc) for doc in dbs.knowledge.search(prompt)]

    context = "\n".join([document_to_context(doc) for doc in knowledge_docs if doc])
    improve_prompt = template.replace("{{ TASK }}", prompt).replace("{{ CONTEXT }}", context)
    dbs.input.append(
        HISTORY_PROMPT_FILE, f"\n[[PROPMT_IMPROVEMNET]]\n{improve_prompt}"
    )
    system = dbs.preprompts["roadmap"] + dbs.preprompts["philosophy"]
    messages = ai.start(system, improve_prompt, step_name=curr_fn())
    
    new_prompt = messages[-1].content.strip()
    new_prompt = solve_prompt_questions(ai, dbs, new_prompt)
    dbs.input[PROMPT_FILE] = new_prompt

    file_list = "\n".join(list(dict.fromkeys([doc.metadata["source"] for doc in knowledge_docs if doc])))
    dbs.project_metadata[FILE_LIST_NAME] = file_list

def get_improve_prompt(ai: AI, dbs: DBs):
    """
    Asks the user what they would like to fix.
    """
    while True:
        current_prompt = get_prompt(ai, dbs)
        opt = input("\n".join([
          "Improve prompt using knowledge? (y/N):"
        ]))
        if not opt or opt.lower() == "n":
          break
        else:
          improve_prompt_with_summary(ai, dbs)

    dbs.input.append(
        HISTORY_PROMPT_FILE, "\n[[PROPMT]]\n%s" % dbs.input[PROMPT_FILE]
    )
    return []