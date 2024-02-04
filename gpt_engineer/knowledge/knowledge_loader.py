from gpt_engineer.settings import (
  GPTENG_PATH,
  VALID_FILE_EXTENSIONS,
  LANGUAGE_FROM_EXTENSION,
  IGNORE_FOLDERS,
  IGNORE_FILES
)
import logging
import os
import time
from datetime import datetime

from langchain.document_loaders.generic import GenericLoader
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter

from gpt_engineer.knowledge.knowledge_code_splitter import KnowledgeCodeSplitter

logger = logging.getLogger(__name__)


class KnowledgeLoader:
    def __init__(self, path):
        self.path = path
        self.glob = "**/*"
        self.suffixes = VALID_FILE_EXTENSIONS + ['']  # Add no-extension files
        self.exclude_folders = list(IGNORE_FOLDERS)
        self.ignore_files = list(IGNORE_FILES)  # Filter out no-extension files
        self.text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=500, chunk_overlap=0
        )
        logger.debug(
            f'KnowledgeLoader initialized {(self.path, self.suffixes)}')

    def should_index_doc(self, file_path, last_update):
        if not last_update:
          return True
        last_doc_update = os.path.getmtime(file_path)
        if last_doc_update > last_update:
          return True
        return False

    def find_files(self, suffixes):
        def valid_file(filename):
          if filename not in self.ignore_files:
            if "." in filename:
              extension = filename.split(".")[-1]
              if f".{extension}" in suffixes:
                return True
          return False
        logger.debug(f'Traversing filesystem {self.path}')
        for root, dirs, files in os.walk(self.path):
            invalid_dirs = [d for d in root.split(
                os.sep) if d in self.exclude_folders]
            if len(invalid_dirs):
              continue
            for filename in files:
                is_valid = valid_file(filename)
                if is_valid:
                  yield os.path.join(root, filename)

    def load(self, last_update: datetime = None):
        logger.debug('Loading knowledge from filesystem')
        documents = []
        code_splitter = KnowledgeCodeSplitter()
        for file_path in list(self.find_files(self.suffixes)):
            new_docs = None
            # Load the knowledge from the filesystem
            if not self.should_index_doc(file_path, last_update):
                continue
            try:
                new_docs = code_splitter.load(file_path)
                loader_type = "code"
            except:
                logger.debug(f"Not available code splitter for {file_path}")

            if not new_docs:
                new_docs = TextLoader(file_path).load_and_split(
                    text_splitter=self.text_splitter)
                for doc in new_docs:
                    doc.metadata["language"] = "txt"
                loader_type = "text"

            if new_docs:
                for doc in new_docs:
                    doc.metadata["loader_type"] = loader_type
                    documents = documents + new_docs 

        logger.debug(f"Loaded {len(documents)} documents")
        return documents
