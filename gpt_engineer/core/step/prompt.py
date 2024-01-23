import logging
from termcolor import colored

from gpt_engineer.core.steps import document_to_context, curr_fn
from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DBs
from gpt_engineer.core.context import validate_context

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

