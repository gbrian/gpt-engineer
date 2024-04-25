"""
gpt_engineer.core
-----------------

The core package for the GPT Engineer project, providing essential modules
and functionalities that form the foundation of the application.

Modules:
    - ai: Contains interfaces to the OpenAI GPT models.
    - domain: Contains type annotations related to the steps workflow in GPT Engineer.
    - chat_to_files: Provides utilities for converting chat model outputs to files.
    - steps: Primary workflow definition & configuration for GPT Engineer.
    - db: Provides file system operations for GPT Engineer projects.

For more specific details, refer to the docstrings within each module.
"""

import logging
import os
import shutil
from pathlib import Path
import openai

from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DB, DBPrompt
from gpt_engineer.core.dbs import DBs, archive
from gpt_engineer.core.steps import run_steps, STEPS, Config as StepsConfig
from gpt_engineer.core.summary import Summary
from gpt_engineer.core.settings import GPTEngineerSettings
from gpt_engineer.cli.collect import collect_learnings
from gpt_engineer.cli.learning import check_collection_consent
from gpt_engineer.cli.file_selector import clear_selected_files_list

from gpt_engineer.settings import GPTENG_PATH, PROMPT_FILE, USE_AI_CACHE


def load_prompt(dbs: DBs):
    if dbs.input.get("prompt"):
        return dbs.input.get("prompt")

    dbs.input[PROMPT_FILE] = input(
        "\nWhat application do you want gpt-engineer to generate?\n"
    )
    return dbs.input.get("prompt")


def preprompts_path() -> Path:
    original_preprompts_path = Path(__file__).parent.parent / "preprompts"
    custom_preprompts_path = Path(f"{GPTENG_PATH}/preprompts")
    if not custom_preprompts_path.exists():
        return original_preprompts_path

    for file in original_preprompts_path.glob("*"):
        if not (custom_preprompts_path / file.name).exists():
            (custom_preprompts_path / file.name).write_text(file.read_text())
        else:
          logging.info("Using local prepromt %s", file.name)
    return custom_preprompts_path

def roles_path() -> Path:
    original_roles_path = Path(__file__).parent.parent / "preprompts/roles"
    custom_roles_path = Path(f"{GPTENG_PATH}/preprompts/roles")
    if not custom_roles_path.exists():
        return original_roles_path

    for file in original_roles_path.glob("*"):
        if not (custom_roles_path / file.name).exists():
            (custom_roles_path / file.name).write_text(file.read_text())
        else:
          logging.info("Using local prepromt %s", file.name)
    return custom_roles_path


def gtp_engineer(settings: GPTEngineerSettings):
    lite_mode = settings.lite_mode
    steps_config = settings.steps_config
    if lite_mode:
        assert not settings.improve_mode, "Lite mode cannot improve code"
        if steps_config == StepsConfig.DEFAULT:
            steps_config = StepsConfig.LITE
    
    if settings.chat_mode:
        steps_config = StepsConfig.CHAT

    if settings.find_files:
        steps_config = StepsConfig.FIND_FILES

    if settings.improve_mode:
        assert (
            steps_config == StepsConfig.DEFAULT
        ), "Improve mode not compatible with other step configs"
        steps_config = StepsConfig.IMPROVE_CODE

    ai = build_ai(settings=settings)
    dbs = build_dbs(settings=settings)

    # Always refresh index to catch user changes
    index_changed = dbs.knowledge.reload()

    if os.path.isfile(settings.prompt_file):
        logging.info("Copying custom prompt %s" % settings.prompt_file)
        shutil.copyfile(settings.prompt_file, "%s/prompt" % settings.prompt_path)
    elif prompt:
        logging.info("Reading prompt from command line")
        user_prompt = input("Override prompt (Optional): ")
        if len(user_prompt) != 0:
          logging.info("Saving custom prompt text")
          with open("%s/prompt" % settings.prompt_path, "a") as f:
              f.write("\n[[PROMPT]]\n" + user_prompt)

    if settings.file_selector:
        clear_selected_files_list(dbs.project_metadata)

    if steps_config not in [
        StepsConfig.EXECUTE_ONLY,
        StepsConfig.USE_FEEDBACK,
        StepsConfig.EVALUATE,
        StepsConfig.IMPROVE_CODE,
        StepsConfig.SELF_HEAL,
        StepsConfig.CHAT,
        StepsConfig.CREATE_PROJECT_SUMMARY,
    ]:
        # archive(dbs)
        # load_prompt(dbs)
        pass

    if settings.update_summary:
      steps = STEPS[StepsConfig.CREATE_PROJECT_SUMMARY]
      run_steps(steps, ai, dbs)
      return

    steps = STEPS[steps_config]
    run_steps(steps, ai, dbs)

    print("Total api cost: $ ", ai.token_usage_log.usage_cost())

    # if check_collection_consent():
    #    collect_learnings(model, temperature, steps, dbs)

    dbs.logs["token_usage"] = ai.token_usage_log.format_log()

    if settings.use_git:
        commit_message = ai.token_usage_log.format_log()
        os.system(f'cd {path} && git add . && git commit -m "{commit_message}"')

def build_ai(settings: GPTEngineerSettings) -> AI:
    return AI(settings=settings)


def build_dbs(settings: GPTEngineerSettings) -> DBs:
    project_path = os.path.abspath(
        settings.project_path
    )  # resolve the string to a valid path (eg "a/b/../c" to "a/c")
    path = Path(project_path).absolute()

    workspace_path = path
    
    project_metadata_path = path 
    if GPTENG_PATH:
        project_metadata_path = Path(GPTENG_PATH).absolute()

    memory_path = project_metadata_path / "memory"
    archive_path = project_metadata_path / "archive"
    prompt_path = project_metadata_path

    preprompts_db = DB(preprompts_path())
    return DBs(
        memory=DB(memory_path),
        logs=DB(memory_path / "logs"),
        input=DBPrompt(prompt_path),
        workspace=DB(workspace_path),
        preprompts=preprompts_db,
        roles=DB(roles_path()),
        archive=DB(archive_path),
        project_metadata=DB(project_metadata_path),
        settings=settings
    )

# Add new function index_content
def index_content(
    path: str,
    extensions: list,
    model: str,
    temperature: float,
    azure_endpoint: str,
):
    """
    Index the content of files in a given path and generate a summary.

    This function walks through the directory specified by the path, and for each file
    with an extension included in the extensions list, it reads the file and generates
    a summary using the AI model.

    Parameters
    ----------
    path : str
        The path of the directory to index.
    extensions : list
        The list of file extensions to include in the indexing.
    model : str
        The name of the AI model to use.
    temperature : float
        The temperature setting for the AI model.
    azure_endpoint : str
        The Azure endpoint URL, if applicable.

    """
    ai = AI(
        model_name=model,
        temperature=temperature,
        azure_endpoint=azure_endpoint,
        cache=DB(memory_path / "cache"),
    )
    summary = Summary(ai)
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(tuple(extensions)):
                with open(os.path.join(root, file), "rb") as f:
                    data = f.read()
                summary.summary_file(file, data)
