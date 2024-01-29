

import logging
import os
import shutil
from pathlib import Path
import openai

from gpt_engineer.core.settings import Settings
from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DB, DBPrompt
from gpt_engineer.core.dbs import DBs, archive
from gpt_engineer.core.steps import run_steps, STEPS, Config as StepsConfig
from gpt_engineer.core.summary import Summary
from gpt_engineer.cli.collect import collect_learnings
from gpt_engineer.cli.learning import check_collection_consent
from gpt_engineer.cli.file_selector import clear_selected_files_list

from gpt_engineer.knowledge.knowledge_prompts import KnowledgePrompts
from gpt_engineer.knowledge.knowledge import Knowledge

from gpt_engineer import settings

class GPTEngineer:
    def __init__(
        self,
        project_path: str = settings.PROJECT_PATH,
        model: str = settings.MODEL,
        temperature: float = settings.TEMPERATURE,
        azure_endpoint: str = settings.AZURE_ENDPOINT,
        use_git: bool = settings.USE_GIT,
        prompt_file: str = settings.PROMPT_FILE,
        verbose: bool = settings.VERBOSE
    ):
        self.project_path = project_path
        self.model = model
        self.temperature = temperature
        self.steps_config = steps_config
        self.improve_mode = improve_mode
        self.lite_mode = lite_mode
        self.azure_endpoint = azure_endpoint
        self.chat_mode = chat_mode
        self.use_git = use_git
        self.role = role
        self.prompt_file = prompt_file
        self.verbose = verbose
        self.prompt = prompt
        self.file_selector = file_selector
        self.rebuild_knowledge = rebuild_knowledge
        self.update_summary = update_summary

        self.ai = AI(
            model_name=self.model,
            temperature=self.temperature,
            azure_endpoint=self.azure_endpoint,
            cache=DB(memory_path / "cache") if USE_AI_CACHE else None,
        )

        # Initialize DBs
        project_path = os.path.abspath(
            project_path
        )  # resolve the string to a valid path (eg "a/b/../c" to "a/c")
        path = Path(project_path).absolute()

        workspace_path = path
        input_path = path

        project_metadata_path = path 
        if GPTENG_PATH:
            project_metadata_path = Path(GPTENG_PATH).absolute()

        memory_path = project_metadata_path / "memory"
        archive_path = project_metadata_path / "archive"
        prompt_path = project_metadata_path

        preprompts_db = DB(preprompts_path())
        knowledge_prompts = KnowledgePrompts(preprompts_db)
        self.dbs = DBs(
            memory=DB(memory_path),
            logs=DB(memory_path / "logs"),
            input=DBPrompt(prompt_path),
            workspace=DB(workspace_path),
            preprompts=preprompts_db,
            roles=DB(roles_path()),
            archive=DB(archive_path),
            project_metadata=DB(project_metadata_path),
            knowledge=Knowledge(workspace_path,
              knowledge_prompts=knowledge_prompts),
            settings=settings
        )


    def run_steps(self, steps_config):
        if self.lite_mode:
            assert not self.improve_mode, "Lite mode cannot improve code"
            if steps_config == StepsConfig.DEFAULT:
                steps_config = StepsConfig.LITE

        if self.chat_mode:
            steps_config = StepsConfig.CHAT

        if self.improve_mode:
            assert (
                steps_config == StepsConfig.DEFAULT
            ), "Improve mode not compatible with other step configs"
            steps_config = StepsConfig.IMPROVE_CODE

        steps = STEPS[steps_config]
        run_steps(steps, self.ai, self.dbs)

    def refresh_knowledge(self):
        if self.rebuild_knowledge:
            # Force full re-build
            self.dbs.knowledge.reset()
        # Always refresh index to catch user changes
        index_changed = self.dbs.knowledge.reload()
        return index_changed

    @staticmethod
    def gpt_engineer(
        project_path: str = settings.PROJECT_PATH,
        model: str = settings.MODEL,
        temperature: float = settings.TEMPERATURE,
        azure_endpoint: str = settings.AZURE_ENDPOINT,
        use_git: bool = settings.USE_GIT,
        prompt_file: str = settings.PROMPT_FILE,
        verbose: bool = settings.VERBOSE
    ) -> 'GPTEngineer':
        return GPTEngineer(
            project_path,
            model,
            temperature,
            azure_endpoint,
            use_git,
            prompt_file,
            verbose
        )