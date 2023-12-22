import logging
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser

from gpt_engineer.settings import (
  GPTENG_PATH,
  VALID_FILE_EXTENSIONS,
  PROJECT_LANGUAGE,
  IGNORE_FOLDERS
)

logger = logging.getLogger(__name__)
class KnowledgeLoader:
    def __init__(self, path):
        self.path = path
        self.glob = "**/*"
        self.suffixes = VALID_FILE_EXTENSIONS
        self.exclude = [f"{key}/*" for key in IGNORE_FOLDERS]
        self.language = PROJECT_LANGUAGE
        logger.debug(f'KnowledgeLoader initialized {(self.path,self.suffixes,self.exclude,self.language)}')

    def load(self):
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
        logger.debug(f'Loaded {len(documents)} documents {[d.metadata for d in documents]}')
        return documents
