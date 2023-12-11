from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser

class KnowledgeLoader:
    def __init__(self, path, glob, suffixes, language):
        self.path = path
        self.glob = glob
        self.suffixes = suffixes
        self.language = language

    @classmethod
    def from_filesystem(cls, path, glob, suffixes, language):
        return cls(path, glob, suffixes, language)

    def load(self):
        # Load the knowledge from the filesystem
        loader = GenericLoader.from_filesystem(
            self.path,
            glob=self.glob,
            suffixes=self.suffixes,
            parser=LanguageParser(language=self.language, parser_threshold=500),
        )
        return loader.load()
