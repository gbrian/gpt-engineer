from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser

class KnowledgeLoader:
    def __init__(self, repo_path, glob, suffixes, language):
        self.repo_path = repo_path
        self.glob = glob
        self.suffixes = suffixes
        self.language = language

    @classmethod
    def from_filesystem(cls, repo_path, glob, suffixes, parser):
        return cls(repo_path, glob, suffixes, parser)

    def load(self):
        # Load the knowledge from the filesystem
        loader = GenericLoader.from_filesystem(
            self.repo_path,
            glob=self.glob,
            suffixes=self.suffixes,
            parser=LanguageParser(language=self.language, parser_threshold=500),
        )
        return loader.load()
