import logging
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser

from gpt_engineer.settings import GPTENG_PATH, VALID_FILE_EXTENSIONS, PROJECT_LANGUAGE


logger = logging.getLogger(__name__)
class KnowledgeLoader:
    def __init__(self, path):
        logger.debug(f'Initializing KnowledgeLoader at {path}')
        self.path = path
        logger.debug(f'Path: {self.path}')
        self.glob = "**/*"
        self.suffixes = VALID_FILE_EXTENSIONS
        self.language = PROJECT_LANGUAGE
        logger.debug('KnowledgeLoader initialized')

    def load(self):
        logger.debug('Loading knowledge from filesystem')
        # Load the knowledge from the filesystem
        loader = GenericLoader.from_filesystem(
            self.path,
            glob=self.glob,
            suffixes=self.suffixes,
            parser=LanguageParser(language=self.language, parser_threshold=500),
        )
        documents = loader.load()
        logger.debug(f'Loaded {len(documents)} documents {[d.metadata for d in documents]}')
        return documents
