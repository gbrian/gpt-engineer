import logging
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser

logger = logging.getLogger(__name__)
class KnowledgeLoader:
    def __init__(self, path, glob, suffixes, language):
        logger.debug(f'Initializing KnowledgeLoader at {path}')
        self.path = path
        logger.debug(f'Path: {self.path}')
        self.glob = glob
        self.suffixes = suffixes
        self.language = language
        logger.debug('KnowledgeLoader initialized')

    @classmethod
    def from_filesystem(cls, path, glob, suffixes, language):
        return cls(path, glob, suffixes, language)

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
        logger.debug(f'Loaded {len(documents)} documents')
        return documents
