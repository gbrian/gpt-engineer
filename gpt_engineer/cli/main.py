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
import subprocess
from pathlib import Path
import traceback

import typer
import sys

from gpt_engineer.core import gtp_engineer, gpt_watch
from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DB, DBPrompt
from gpt_engineer.core.dbs import DBs, archive
from gpt_engineer.core.steps import STEPS, Config as StepsConfig
from gpt_engineer.core.settings import GPTEngineerSettings
from gpt_engineer.cli.collect import collect_learnings
from gpt_engineer.cli.learning import check_collection_consent

from gpt_engineer.settings import OPENAI_API_KEY, MODEL, TEMPERATURE

app = typer.Typer()  # creates a CLI app


@app.command()
def parse_args(
    project_path: str = typer.Argument(".", help="path"),
    model: str = typer.Option(MODEL, "--model", "-m", help="model id string"),
    temperature: float = TEMPERATURE,
    steps_config: StepsConfig = typer.Option(
        StepsConfig.DEFAULT, "--steps", "-s", help="decide which steps to run"
    ),
    role: str = typer.Option(
        "analyst",
        "-r",
        "--role",
        help="Specify the user role.",
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
    chat_mode: bool = typer.Option(
        False,
        "--chat",
        "-c",
        help="Chat mode.",
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
        "-pf",
        help="Use this prompt. This will replace workspce's prompt with file contents.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    prompt: bool = typer.Option(False, "--prompt-text", "-p", help="Custom prompt text."),
    file_selector: bool = typer.Option(
        False, "--file-selector", "-f", help="Force the request of files affected."
    ),
    api: bool = typer.Option(
        False, "--api", help="Run GPT Engineer API."
    ),
    port: int = typer.Option(8066,
      "--port",
      help="API port"
    ),
    test: str = typer.Option(
        "",
        "--test",
        "-t",
        help="Script file or command to execute after all steps. If the test exits with non-zero code run all over again.",
    ),
    build_knowledge: bool = typer.Option(
        False,
        "--build-knowledge",
        "-B",
        help="Build knowledge base.",
    ),
    update_summary: bool =  typer.Option(
        False,
        "--summary",
        "-S",
        help="Build knowledge summary.",
    ),
    find_files: bool =  typer.Option(
        False,
        "--find-files",
        "-f",
        help="Find files affected by the prompt",
    ),
    watch: str =  typer.Option(
        False,
        "--watch",
        "-w",
        help="watches for chanes in a folder",
    )
):
  settings = GPTEngineerSettings(**locals())
  logging.info(f"ARGS {settings.__dict__}")
  if settings.api:
    run_api(settings=settings)
  elif settings.watch:
    gpt_watch(settings=settings)
  else:
    run_main(settings=settings)

def run_api(settings: GPTEngineerSettings):
    envs = settings.to_env()
    command = f"{' '.join(envs)} uvicorn main:app --host 0.0.0.0 --port {settings.port} --reload --reload-dir {settings.project_path}"
    logging.info(f"API MODE: {command}")
    os.system(command)
    return

def run_main(settings: GPTEngineerSettings):
    while True:
        gtp_engineer(settings)

        if test:
            print("Starting test execution...")
            if os.path.isfile(test):
                result = subprocess.run(test, shell=True, capture_output=True)
            else:
                result = subprocess.run(test, shell=True, capture_output=True, executable="/bin/bash")
            print("Test stdout:\n", result.stdout.decode())
            print("Test stderr:\n", result.stderr.decode())
            if result.returncode == 0:
                print("Test execution passed.")
                break
            else:
                print("Test execution failed.")
        else:
            break


if __name__ == "__main__":
        while True:
            logging.info(f"CLI MODE")
            try:
                app()
            except KeyboardInterrupt:
                break
            except Exception as ex:
                print(f"Error running gpt-engineer {ex}")
                traceback.print_exception(ex)
