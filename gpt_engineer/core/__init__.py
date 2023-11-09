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
from gpt_engineer.core.steps import STEPS, Config as StepsConfig
from gpt_engineer.cli.collect import collect_learnings
from gpt_engineer.cli.learning import check_collection_consent


def preprompts_path(use_custom_preprompts: bool, input_path: Path = None) -> Path:
    original_preprompts_path = Path(__file__).parent.parent / "preprompts"
    if not use_custom_preprompts:
        return original_preprompts_path

    custom_preprompts_path = input_path / "preprompts"
    if not custom_preprompts_path.exists():
        custom_preprompts_path.mkdir()

    for file in original_preprompts_path.glob("*"):
        if not (custom_preprompts_path / file.name).exists():
            (custom_preprompts_path / file.name).write_text(file.read_text())
    return custom_preprompts_path


def gtp_engineer(
    project_path: str,
    model: str,
    temperature: float,
    steps_config: StepsConfig,
    improve_mode: bool,
    lite_mode: bool,
    azure_endpoint: str,
    use_custom_preprompts: bool,
    ai_cache: bool,
    use_git: bool,
    prompt_file: str,
    verbose: bool,
    prompt: str,
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
                "use_custom_preprompts": use_custom_preprompts,
                "ai_cache": ai_cache,
                "use_git": use_git,
                "prompt_file": prompt_file,
                "verbose": verbose,
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

    if os.path.isfile(prompt_file):
        logging.info("Copying custom prompt %s" % prompt_file)
        shutil.copyfile(prompt_file, "%s/prompt" % path)

    project_metadata_path = path / ".gpteng"
    memory_path = project_metadata_path / "memory"
    archive_path = project_metadata_path / "archive"

    dbs = DBs(
        memory=DB(memory_path),
        logs=DB(memory_path / "logs"),
        input=DBPrompt(input_path),
        workspace=DB(workspace_path),
        preprompts=DB(preprompts_path(use_custom_preprompts, input_path)),
        archive=DB(archive_path),
        project_metadata=DB(project_metadata_path),
    )

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
    for step in steps:
        messages = step(ai, dbs)
        dbs.logs[step.__name__] = AI.serialize_messages(messages)

    print("Total api cost: $ ", ai.token_usage_log.usage_cost())

    if check_collection_consent():
        collect_learnings(model, temperature, steps, dbs)

    dbs.logs["token_usage"] = ai.token_usage_log.format_log()

    if use_git:
        commit_message = ai.token_usage_log.format_log()
        os.system(f'cd {path} && git add . && git commit -m "{commit_message}"')
