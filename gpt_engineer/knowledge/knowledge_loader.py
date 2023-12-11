import glob
import os

class KnowledgeLoader:
    def __init__(self, repo_path, glob, suffixes, parser):
        self.repo_path = repo_path
        self.glob = glob
        self.suffixes = suffixes
        self.parser = parser

    @classmethod
    def from_filesystem(cls, repo_path, glob, suffixes, parser):
        return cls(repo_path, glob, suffixes, parser)

    def load(self):
        # Load the knowledge from the filesystem
        documents = []
        for filename in glob.glob(os.path.join(self.repo_path, self.glob), recursive=True):
            with open(filename, 'r') as file:
                documents.append(file.read())
        return documents