import logging
import os
import time
from datetime import datetime

from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import Language

CURRENT_SPLITTER_LANGUAGES = [lang.lower() for lang in dir(Language)]


from gpt_engineer.settings import (
  GPTENG_PATH,
  VALID_FILE_EXTENSIONS,
  LANGUAGE_FROM_EXTENSION,
  IGNORE_FOLDERS,
  IGNORE_FILES
)

logger = logging.getLogger(__name__)
class KnowledgeLoader:
    def __init__(self, path):
        self.path = path
        self.glob = "**/*"
        self.suffixes = VALID_FILE_EXTENSIONS + [''] # Add no-extension files
        self.exclude_folders = list(IGNORE_FOLDERS)
        self.ignore_files = list(IGNORE_FILES) # Filter out no-extension files
        self.text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=100, chunk_overlap=0
        )
        logger.debug(f'KnowledgeLoader initialized {(self.path, self.suffixes)}')

    def should_index_doc (self, file_path, last_update):
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
            invalid_dirs = [d for d in root.split(os.sep) if d in self.exclude_folders]
            if len(invalid_dirs):
              continue
            for filename in files:
                is_valid = valid_file(filename)
                if is_valid:
                  yield os.path.join(root, filename)
        
    def load(self, last_update: datetime = None):
        logger.debug('Loading knowledge from filesystem')
        documents = []
        for file_path in list(self.find_files(self.suffixes)):
          # Load the knowledge from the filesystem
          suffix = file_path.split(".")[-1] if "." in file_path else ""
          language = LANGUAGE_FROM_EXTENSION.get(suffix)
          new_docs = None
          loader_type = None
          if not self.should_index_doc(file_path, last_update):
            continue
          try:
            try:
              if language and language in CURRENT_SPLITTER_LANGUAGES:
                parser = LanguageParser(language=language, parser_threshold=500)
                loader = GenericLoader.from_filesystem(
                    file_path,
                    parser=parser
                )
                new_docs = loader.load()
                loader_type = "code"
            except KeyError:
              logger.debug(f"Not available language parser for {suffix}")

            if not new_docs:  
              new_docs = TextLoader(file_path).load_and_split(text_splitter=self.text_splitter)
              loader_type = "text"
          except Exception as ex:
            logger.error(f"Error loading file {file_path} {ex}")

          if new_docs:
            for doc in new_docs:
              doc.metadata["language"] = language if language else ""
              doc.metadata["loader_type"] = loader_type
            documents = documents + new_docs 

        logger.debug(f"Loaded {len(documents)} documents")
        return documents
