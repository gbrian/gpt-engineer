import logging
from termcolor import colored

from gpt_engineer.core.steps import document_to_context, curr_fn, validate_context
from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DBs

from gpt_engineer.core.step.chat import chat_interaction

from gpt_engineer.settings import (
  PROMPT_FILE,
  HISTORY_PROMPT_FILE,
  PROJECT_SUMMARY,
  LANGUAGE_FROM_EXTENSION,
)

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

def set_prompt (dbs: DBs, new_prompt: str):
  dbs.input[PROMPT_FILE] = new_prompt

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