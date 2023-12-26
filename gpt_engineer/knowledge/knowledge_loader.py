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
        logger.debug(f'KnowledgeLoader initialized {(self.path, self.suffixes)}')

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
        documents = []
        for suffix in self.suffixes:
          # Load the knowledge from the filesystem
          language = LANGUAGE_FROM_EXTENSION.get(suffix)
          new_docs = None

          try:
            if language and language in CURRENT_SPLITTER_LANGUAGES:
              parser = LanguageParser(language=language, parser_threshold=500)
              loader = GenericLoader.from_filesystem(
                  self.path,
                  glob=self.glob,
                  suffixes=[suffix],
                  parser=parser,
                  show_progress=True
              )
              new_docs = loader.load()
          except KeyError:
            logger.debug(f"Not available language parser for {suffix}")

          if not new_docs:  
            loader = DirectoryLoader(self.path, glob=f"**/*{suffix}", loader_cls=TextLoader)
            new_docs = loader.load()
            if language:
                for doc in new_docs:
                  doc.metadata["language"] = language
          documents = documents + new_docs 

        # Flatten the results before returning them
        documents = [doc for doc in documents if self.should_index_doc(doc, last_update)]
        return documents
