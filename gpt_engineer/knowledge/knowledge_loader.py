import logging
import os
from datetime import datetime

from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser

from gpt_engineer.settings import (
  GPTENG_PATH,
  VALID_FILE_EXTENSIONS,
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
        self.language = PROJECT_LANGUAGE
        logger.debug(f'KnowledgeLoader initialized {(self.path,self.suffixes,self.language)}')

    def should_index_doc (self, doc, last_update):
          source = doc.metadata["source"]
          if source.split("/")[-1] in IGNORE_FILES:
            return False
          if len([ignore_folder for ignore_folder in IGNORE_FOLDERS if f"{ignore_folder}/" in source]) != 0:
            return False
          if not last_update:
            return True
          last_doc_update = os.path.getmtime(source)
          return True if last_doc_update > last_update else False
        
    def load(self, last_update: datetime = None):
        logger.debug('Loading knowledge from filesystem')
        # Load the knowledge from the filesystem
        loader = GenericLoader.from_filesystem(
            self.path,
            glob=self.glob,
            suffixes=self.suffixes,
            parser=LanguageParser(language=self.language, parser_threshold=500),
            show_progress=True
        )
        documents = loader.load()
        # Flatten the results before returning them
        documents = [doc for doc in documents if self.should_index_doc(doc, last_update)]
        return documents
