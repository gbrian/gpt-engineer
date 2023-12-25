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
        self.exclude = [f"{key}/*" for key in IGNORE_FOLDERS] + [f"{key}/*" for key in IGNORE_FILES]
        self.language = PROJECT_LANGUAGE
        logger.debug(f'KnowledgeLoader initialized {(self.path,self.suffixes,self.exclude,self.language)}')

    def load(self, last_update: datetime = None):
        logger.debug('Loading knowledge from filesystem')
        # Load the knowledge from the filesystem
        loader = GenericLoader.from_filesystem(
            self.path,
            glob=self.glob,
            suffixes=self.suffixes,
            exclude=self.exclude,
            parser=LanguageParser(language=self.language, parser_threshold=500),
            show_progress=True
        )
        documents = loader.load()
        # Flatten the results before returning them
        def should_index_doc (doc):
          if not last_update:
            return True
          last_doc_update = os.path.getmtime(doc.metadata["source"])
          return True if last_doc_update > last_update else False
        
        documents = [doc for doc in documents if should_index_doc(doc)]
        return documents
