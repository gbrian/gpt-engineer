import logging
import re
from termcolor import colored

from gpt_engineer.core.ai import AI
from gpt_engineer.core.dbs import DBs
from gpt_engineer.core.step.prompt import get_prompt, set_prompt
from gpt_engineer.core.step.chat import ai_chat
from gpt_engineer.core.utils import document_to_context, curr_fn
from gpt_engineer.core.context import parallel_validate_contexts

from gpt_engineer.preprompts import (
    ROADMAP,
    BUSINESS_REQUEST_DOCUMENT,
    CLARIFY_BUSINESS_REQUEST,
    ANALIST_ROLE,
)

from gpt_engineer.settings import (
    HISTORY_PROMPT_FILE,
)

MORE_INFO_IS_NEEDED = "MORE INFO NEEDED"
USER_FEEDBACK = "USER FEEDBACK:"

QUESTION_PREFIX = re.compile(r"^\s*[0-9-.]+\.? ")


def clarify_business_request(ai: AI, dbs: DBs):
    prompt = get_prompt(ai, dbs)
    dbs.input.append(HISTORY_PROMPT_FILE, f"\n[[PROMPT]]\n{prompt}")
    if input(f"Clarify prompt (y/N):") != "y":
        return prompt, None

    clarify_template = dbs.preprompts["clarify_business_request"]

    auto_response = None
    ai_response = None
    while True:
        documents = dbs.knowledge.search(prompt)
        documents = [
            doc for doc in parallel_validate_contexts(dbs, prompt, documents) if doc
        ]
        context = "\n".join([document_to_context(doc) for doc in documents])

        prompt = clarify_template.replace("{{ context }}", context).replace(
            "{{ prompt }}", prompt
        )

        messages = ai.start("", prompt, step_name=curr_fn())

        ai_response = messages[-1].content.strip()
        ai_response, comments = solve_prompt_questions(
            ai, dbs, ai_response, auto_response
        )
        if not auto_response and not comments:
            comments = input(
                "\n".join(
                    [
                        colored("ANALYST", "green"),
                        ai_response,
                        "",
                        colored(
                            "check the generated user story and write comments if needed",
                            "green",
                        ),
                        colored(
                            "Use '@ai: your_question...' to ask ai for help", "green"
                        ),
                        colored("Or just press Enter to continue", "green"),
                        colored(">", "green"),
                    ]
                )
            )
            if not comments:
                break
        prompt = f"{ai_response}\nCOMMNENTS:\n{comments}"
    return prompt, ai_response

def clarify_search_request (ai: AI, dbs: DBs, prompt: str):
  dbs.input.append(
    HISTORY_PROMPT_FILE, f"\n[[PROMPT]]\n{prompt}"
  )
  
  clarify_search = dbs.preprompts["clarify_search_request"]
  
  search = clarify_search.replace("{{ prompt }}", prompt)
  messages = ai.start("", search, step_name=curr_fn())
  ai_response = messages[-1].content.strip()
  return ai_response

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

    more_info_needed = prompt.split(MORE_INFO_IS_NEEDED)[-1]
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


def solve_prompt_questions(ai: AI, dbs: DBs, prompt: str, auto_response=None):
    questions = get_more_info_needed(prompt)
    has_comments = True if questions is not None and len(questions) else False

    if not has_comments:
        return prompt, has_comments

    logging.debug(f"Solving prompt questions")
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
            ": ",
        ]
        print()
        opt = auto_response if auto_response else input("\n".join(question_request))
        logging.debug(f"User response: {opt}")
        response = opt
        if opt.lower() == "@ai":
            response = ai_chat(ai, dbs, user_input=question, messages=[prompt])

        qas.append((question, response))

    prompt = replace_more_info_by_user_feedback(prompt, qas)
    return prompt, True
