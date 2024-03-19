
import logging
import os
import time
import subprocess
from datetime import datetime

from langchain.document_loaders.generic import GenericLoader
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter

from gpt_engineer.core.settings import GPTEngineerSettings
from gpt_engineer.knowledge.knowledge_code_splitter import KnowledgeCodeSplitter

logger = logging.getLogger(__name__)


class KnowledgeLoader:
    def __init__(self, settings: GPTEngineerSettings):
        self.path = settings.project_path
        self.settings = settings
        self.text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=500, chunk_overlap=0
        )
        logger.debug(
            f'KnowledgeLoader initialized {(self.path)}')

    def should_index_doc(self, file_path, last_update):
        if not last_update:
          return True
        last_doc_update = os.path.getmtime(file_path)
        if last_doc_update > last_update:
          return True
        return False

    def load(self, last_update: datetime = None, path: str = None):
        logger.debug('Loading knowledge from filesystem')
        documents = []
        code_splitter = KnowledgeCodeSplitter()
        files = self.list_repository_files(last_update=last_update, path=path)
        for file_path in files:
            new_docs = code_splitter.load(file_path)
            if not new_docs:
                continue
            documents = documents + new_docs

        logger.debug(f"Loaded {len(documents)} documents from {len(files)} files")
        return documents

    def _run_git_command(self, command):
        result = subprocess.run(command, cwd=self.path, stdout=subprocess.PIPE)
        file_paths = result.stdout.decode('utf-8').split('\n')
        return file_paths

    def list_repository_files(self, last_update, path: str = None):
        # Versioned files
        versioned_files = self._run_git_command(['git', 'ls-files'])

        # Unversioned files
        unversioned_files = self._run_git_command(['git', 'ls-files', '--others', '--exclude-standard'])

        # joining versioned and unversioned file paths
        full_file_paths = [os.path.join(self.path, file_path) for file_path in versioned_files + unversioned_files if file_path]
        def isValidFile(file):
            if path:
                if not path in file:
                    return False

            if not self.should_index_doc(file, last_update):
                logging.info(f"INVALID FILE should_index_doc {file} {last_update}")
                return False
            if [err for err in self.settings.knowledge_file_ignore if err in file]:
                logging.info(f"INVALID FILE knowledge_file_ignore {file}")
                return False
            return True

        full_file_paths = [file for file in full_file_paths if isValidFile(file) ]
        return full_file_paths