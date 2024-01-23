import logging
import re
from termcolor import colored

from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DBs
from gpt_engineer.core.step.prompt import get_prompt, set_prompt
from gpt_engineer.core.step.chat import ai_chat
from gpt_engineer.core.steps import document_to_context, curr_fn

from gpt_engineer.preprompts import (
  ROADMAP,
  BUSINESS_REQUEST_DOCUMENT,
  CLARIFY_BUSINESS_REQUEST,
  ANALIST_ROLE
)

from gpt_engineer.settings import (
  HISTORY_PROMPT_FILE,
)

MORE_INFO_IS_NEEDED="MORE INFO IS NEEDED"
USER_FEEDBACK="USER FEEDBACK:"

QUESTION_PREFIX = re.compile(r"^\s*[0-9-.]+\.? ")

def clarify_business_request (ai: AI, dbs: DBs):
  system = dbs.roles[f"{dbs.settings.role}.md"] 
  prompt = get_prompt(ai, dbs)

  dbs.input.append(
    HISTORY_PROMPT_FILE, f"\n[[PROMPT]]\n{prompt}"
  )

  if input(f"Clarify prompt with {dbs.settings.role} (Y/n):") == 'n':
    return prompt, None

  logging.debug(f"[clarify_business_request]: {system} - {prompt}")

  prompt, _ = ai_chat(ai, dbs, user_input=prompt, messages=[], system=system)
  
  messages = ai.start(system, prompt, step_name=curr_fn()) 
  auto_response = None
  while True:
    user_message = messages[-2].content.strip() 
    ai_response = messages[-1].content.strip()
    ai_response, comments = solve_prompt_questions(ai, dbs, ai_response, auto_response)
    if not auto_response and not comments:
      comments = input("\n".join([
        colored("BUSINESS USER:", "green"),
        prompt,
        colored("ANALYST", "green"),
        ai_response,
        "",
        colored("check the generated user story and write cooments if needed", "green"),
        colored("Use '@ai: your_question...' to ask ai for help", "green"),
        colored("Or just press Enter to continue", "green"),
        colored(">", "green")
      ]))
      if not comments:
        return prompt, ai_response
      elif comments.startswith("@ai"):
        comments = ai.next(messages, prompt=comments, step_name=curr_fn())[-1].content.strip()
    auto_response = None
    messages = ai.next(messages, prompt=comments, step_name=curr_fn())
  return prompt, None

def get_more_info_needed(prompt):
  if MORE_INFO_IS_NEEDED not in prompt:
    return None
  def is_q(question):
      question = question.strip()
      if len(question):
        if QUESTION_PREFIX.match(question):
          return True
        # logging.debug(f"{question} IS NOT A QUESTION")
      return False
  
  more_info_needed = prompt.split(MORE_INFO_IS_NEEDED)[1]
  more_info_questions = more_info_needed.split("\n")
  questions = [question for question in more_info_questions if is_q(question)]
  logging.debug(f"[get_more_info_needed]:\n{more_info_questions}\n{questions}")
  return questions  

def replace_more_info_by_user_feedback(prompt, qas):
  for question, response in qas:
    if not response:
      prompt = prompt.replace(question, "")
    else:
      prompt = prompt.replace(question, f"Q: {question}\nA: {response}\n")
    prompt = prompt.replace(MORE_INFO_IS_NEEDED, USER_FEEDBACK)

  return prompt

def build_userfeedback(qas):
  user_feedback = [USER_FEEDBACK]
  for question, response in qas:
    user_feedback.append(f"Q: {question}")
    user_feedback.append(f"A: {response}")
  return "\n".join(user_feedback)

def solve_prompt_questions(ai:AI, dbs: DBs, prompt: str, auto_response=None):
    has_comments = False
    if MORE_INFO_IS_NEEDED not in prompt:
      return prompt, has_comments

    def is_q(question):
      question = question.strip()
      if len(question):
        return True if question[0] == '-' else False
      return False
  
    logging.debug(f"Solving prompt questions")
    questions = get_more_info_needed(prompt)
    logging.debug(f"Questions: {questions}")
    qas = []
    for question in questions:
      question_request = [
        "*** QUESTION *******************************************",
        f"{question}",
        "********************************************************",
        "Write @AI to ask AI to help (chat mode)",
        "write your own answer",
        "Leave blank to remove the question",
        ": "
      ]
      print()
      opt = auto_response if auto_response else input("\n".join(question_request))
      logging.debug(f"User response: {opt}")
      response = opt
      if opt.lower() == '@ai':
        response = ai_chat(ai, dbs, user_input=question, messages=[prompt])

      qas.append((question, response))
    
    prompt = replace_more_info_by_user_feedback(prompt, qas)
    user_feedback = build_userfeedback([qa for qa in qas if qa[1]])
    return prompt, user_feedback