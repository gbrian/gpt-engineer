import logging
import os
from datetime import datetime

from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import Language

CURRENT_SPLITTER_LANGUAGES = [lang.lower() for lang in dir(Language)]


from gpt_engineer.settings import (
  GPTENG_PATH,
  VALID_FILE_EXTENSIONS,
  LANGUAGE_FROM_EXTENSION,
  PROJECT_LANGUAGE,
  IGNORE_FOLDERS,
  IGNORE_FILES
)

logger = logging.getLogger(__name__)
class KnowledgeLoader:
    def __init__(self, path):
        self.path = path
        self.glob = "**/*"
        self.suffixes = VALID_FILE_EXTENSIONS
        self.exclude_folders = list(IGNORE_FOLDERS)
        logger.debug(f'KnowledgeLoader initialized {(self.path, self.suffixes)}')

    def should_index_doc (self, file_path, last_update):
          if not last_update:
            return True
          last_doc_update = os.path.getmtime(file_path)
          return True if last_doc_update > last_update else False

    def find_files(self, extension):
        # logger.debug(f'Traversing filesystem {self.path} ignoring {self.exclude_folders}')
        for root, dirs, files in os.walk(self.path):
            invalid_dirs = [d for d in root.split(os.sep) if d in self.exclude_folders]
            if len(invalid_dirs):
              continue
            # logger.debug(f'Traversing filesystem {root}')
            for filename in files:
                if filename.endswith(extension):
                  yield os.path.join(root, filename)
        
    def load(self, last_update: datetime = None):
        logger.debug('Loading knowledge from filesystem')
        documents = []
        for suffix in self.suffixes:
          # Load the knowledge from the filesystem
          language = LANGUAGE_FROM_EXTENSION.get(suffix)
          new_docs = None
          file_paths = list(self.find_files(suffix))
          for file_path in file_paths:
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
              except KeyError:
                logger.debug(f"Not available language parser for {suffix}")

              if not new_docs:  
                new_docs = TextLoader(file_path).load()
            

              if language:
                  for doc in new_docs:
                    doc.metadata["language"] = language
            except Exception as ex:
              logger.error(f"Error loading file {file_path} {ex}")

            if new_docs:
              documents = documents + new_docs 

        logger.debug(f"Loaded {len(documents)} documents")
        return documents
