import os

from gpt_engineer.core.settings import GPTEngineerSettings

class WikiManager:
    def __init__(self, settings: GPTEngineerSettings):
        self.settings = settings

    def update_wiki(self, file_path):
        
