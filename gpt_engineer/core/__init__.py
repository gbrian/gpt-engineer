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
from gpt_engineer.core.db import DB, DBs, DBPrompt, archive
from gpt_engineer.core.steps import run_steps, STEPS, Config as StepsConfig
from gpt_engineer.core.summary import Summary
from gpt_engineer.cli.collect import collect_learnings
from gpt_engineer.cli.learning import check_collection_consent
from gpt_engineer.cli.file_selector import clear_selected_files_list

from gpt_engineer.settings import GPTENG_PATH, PROMPT_FILE


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


def gtp_engineer(
    project_path: str,
    model: str,
    temperature: float,
    steps_config: StepsConfig,
    improve_mode: bool,
    lite_mode: bool,
    azure_endpoint: str,
    ai_cache: bool,
    use_git: bool,
    prompt_file: str,
    verbose: bool,
    prompt: str,
    file_selector: bool,
):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    logging.debug(
        "gpt_engineer %s"
        % str(
            {
                "project_path": project_path,
                "model": model,
                "temperature": temperature,
                "steps_config": steps_config,
                "improve_mode": improve_mode,
                "lite_mode": lite_mode,
                "azure_endpoint": azure_endpoint,
                "ai_cache": ai_cache,
                "use_git": use_git,
                "prompt_file": prompt_file,
                "verbose": verbose,
                "prompt": prompt,
                "file_selector": file_selector,
            }
        )
    )

    if lite_mode:
        assert not improve_mode, "Lite mode cannot improve code"
        if steps_config == StepsConfig.DEFAULT:
            steps_config = StepsConfig.LITE

    if improve_mode:
        assert (
            steps_config == StepsConfig.DEFAULT
        ), "Improve mode not compatible with other step configs"
        steps_config = StepsConfig.IMPROVE_CODE

    project_path = os.path.abspath(
        project_path
    )  # resolve the string to a valid path (eg "a/b/../c" to "a/c")
    path = Path(project_path).absolute()
    print("Running gpt-engineer in", path, "\n")

    workspace_path = path
    input_path = path

    project_metadata_path = path 
    if GPTENG_PATH:
        project_metadata_path = Path(GPTENG_PATH).absolute()

    memory_path = project_metadata_path / "memory"
    archive_path = project_metadata_path / "archive"
    prompt_path = project_metadata_path

    dbs = DBs(
        memory=DB(memory_path),
        logs=DB(memory_path / "logs"),
        input=DBPrompt(prompt_path),
        workspace=DB(workspace_path),
        preprompts=DB(preprompts_path()),
        archive=DB(archive_path),
        project_metadata=DB(project_metadata_path),
    )

    if os.path.isfile(prompt_file):
        logging.info("Copying custom prompt %s" % prompt_file)
        shutil.copyfile(prompt_file, "%s/prompt" % prompt_path)
    elif prompt:
        logging.info("Reading prompt from command line")
        user_prompt = input("Override prompt (Optional): ")
        if len(user_prompt) != 0:
          logging.info("Saving custom prompt text")
          with open("%s/prompt" % prompt_path, "a") as f:
              f.write("\n[[PROMPT]]\n" + user_prompt)

    if file_selector:
        clear_selected_files_list(dbs.project_metadata)

    ai = AI(
        model_name=model,
        temperature=temperature,
        azure_endpoint=azure_endpoint,
        cache=DB(memory_path / "cache") if ai_cache else None,
    )

    if steps_config not in [
        StepsConfig.EXECUTE_ONLY,
        StepsConfig.USE_FEEDBACK,
        StepsConfig.EVALUATE,
        StepsConfig.IMPROVE_CODE,
        StepsConfig.SELF_HEAL,
    ]:
        archive(dbs)
        load_prompt(dbs)

    steps = STEPS[steps_config]
    run_steps(steps, ai, dbs)

    print("Total api cost: $ ", ai.token_usage_log.usage_cost())

    # if check_collection_consent():
    #    collect_learnings(model, temperature, steps, dbs)

    dbs.logs["token_usage"] = ai.token_usage_log.format_log()

    if use_git:
        commit_message = ai.token_usage_log.format_log()
        os.system(f'cd {path} && git add . && git commit -m "{commit_message}"')


# Add new function index_content
def index_content(
    path: str,
    extensions: list,
    model: str,
    temperature: float,
    azure_endpoint: str,
    ai_cache: bool,
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
    ai_cache : bool
        Whether to use AI cache.

    """
    ai = AI(
        model_name=model,
        temperature=temperature,
        azure_endpoint=azure_endpoint,
        cache=DB(memory_path / "cache") if ai_cache else None,
    )
    summary = Summary(ai)
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(tuple(extensions)):
                with open(os.path.join(root, file), "rb") as f:
                    data = f.read()
                summary.summary_file(file, data)
