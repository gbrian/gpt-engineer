
import logging
import os
import time
import subprocess
import pathlib
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

    def should_index_doc(self, file_path, last_update, current_sources=None):
        if not last_update:
            return True
        if current_sources and file_path not in current_sources:
            return True
        last_doc_update = os.path.getmtime(file_path)
        if last_doc_update > last_update:
          return True
        return False

    def load(self, last_update: datetime = None, path: str = None, current_sources=None):
        logger.debug(f"Loading knowledge from filesystem, last_update: {last_update} path: {path}")
        documents = []
        code_splitter = KnowledgeCodeSplitter()
        files = self.list_repository_files(last_update=last_update, path=path, current_sources=[])
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

    def list_repository_files(self, last_update, path: str = None, current_sources=None):
        logger.debug(f"list_repository_files, last_update: {last_update} path: {path} current_sources: {current_sources}")
        
        full_file_paths = None
        if path:
            full_file_paths = [str(file_path) for file_path in pathlib.Path(path).rglob("*")]
            logging.info(f"Indexing {full_file_paths}")
        else:
            # Versioned files
            versioned_files = self._run_git_command(['git', 'ls-files'])
            # Unversioned files
            unversioned_files = self._run_git_command(['git', 'ls-files', '--others', '--exclude-standard'])

            # joining versioned and unversioned file paths
            full_file_paths = [os.path.join(self.path, file_path) for file_path in versioned_files + unversioned_files]

        def isValidFile(file):
            if path:
                if not (path in file):
                    return False
            
            file_errors = [err for err in self.settings.knowledge_file_ignore.split(",") if err in file]
            if file_errors:
                return False
            
            if not self.should_index_doc(file_path=file, last_update=last_update, current_sources=[]):
                return False
            
            return True

        full_file_paths = [file for file in full_file_paths if isValidFile(file) ]
        return full_file_paths