"""
This module provides a CLI tool to interact with the GPT Engineer application,
enabling users to use OpenAI's models and define various parameters for the
project they want to generate, improve or interact with.

Main Functionality:
---------------------
- Load environment variables needed to work with OpenAI.
- Allow users to specify parameters such as:
  - Project path
  - Model type (default to GPT-4)
  - Temperature
  - Step configurations
  - Code improvement mode
  - Lite mode for lighter operations
  - Azure endpoint for Azure OpenAI services
  - Using project's preprompts or default ones
  - Verbosity level for logging
- Interact with AI, databases, and archive processes based on the user-defined parameters.

Notes:
- Ensure the .env file has the `OPENAI_API_KEY` or provide it in the working directory.
- The default project path is set to `projects/example`.
- For azure_endpoint, provide the endpoint for Azure OpenAI service.

"""

import logging
import os
import shutil
from pathlib import Path

import openai
import typer
from dotenv import load_dotenv

from gpt_engineer.core import gtp_engineer
from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DB, DBs, DBPrompt, archive
from gpt_engineer.core.steps import STEPS, Config as StepsConfig
from gpt_engineer.cli.collect import collect_learnings
from gpt_engineer.cli.learning import check_collection_consent

app = typer.Typer()  # creates a CLI app


def load_env_if_needed():
    if os.getenv("OPENAI_API_KEY") is None:
        load_dotenv()
    if os.getenv("OPENAI_API_KEY") is None:
        # if there is no .env file, try to load from the current working directory
        load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))
    openai.api_key = os.getenv("OPENAI_API_KEY")


def load_prompt(dbs: DBs):
    if dbs.input.get("prompt"):
        return dbs.input.get("prompt")

    dbs.input["prompt"] = input(
        "\nWhat application do you want gpt-engineer to generate?\n"
    )
    return dbs.input.get("prompt")


@app.command()
def main(
    project_path: str = typer.Argument("projects/example", help="path"),
    model: str = typer.Argument("gpt-4", help="model id string"),
    temperature: float = 0.1,
    steps_config: StepsConfig = typer.Option(
        StepsConfig.DEFAULT, "--steps", "-s", help="decide which steps to run"
    ),
    improve_mode: bool = typer.Option(
        False,
        "--improve",
        "-i",
        help="Improve code from existing project.",
    ),
    lite_mode: bool = typer.Option(
        False,
        "--lite",
        "-l",
        help="Lite mode - run only the main prompt.",
    ),
    azure_endpoint: str = typer.Option(
        "",
        "--azure",
        "-a",
        help="""Endpoint for your Azure OpenAI Service (https://xx.openai.azure.com).
            In that case, the given model is the deployment name chosen in the Azure AI Studio.""",
    ),
    use_custom_preprompts: bool = typer.Option(
        False,
        "--use-custom-preprompts",
        help="""Use your project's custom preprompts instead of the default ones.
          Copies all original preprompts to the project's workspace if they don't exist there.""",
    ),
    ai_cache: bool = typer.Option(
        False,
        "--cache",
        "-c",
        help="Caches AI responses.",
    ),
    use_git: bool = typer.Option(
        False,
        "--git",
        "-g",
        help="Project uses git. Commit changes to keep track and easy changes detection.",
    ),
    prompt_file: str = typer.Option(
        False,
        "--prompt",
        "-p",
        help="Use this prompt. This will replace workspce's prompt with file contents.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    load_env_if_needed()

    gtp_engineer(
        project_path=project_path,
        model=model,
        temperature=temperature,
        steps_config=steps_config,
        improve_mode=improve_mode,
        lite_mode=lite_mode,
        azure_endpoint=azure_endpoint,
        use_custom_preprompts=use_custom_preprompts,
        ai_cache=ai_cache,
        use_git=use_git,
        prompt_file=prompt_file,
        verbose=verbose,
    )


if __name__ == "__main__":
    app()
