import logging
from langchain.embeddings.openai import OpenAIEmbeddings
from gpt_engineer.knowledge.knowledge_loader import KnowledgeLoader
from langchain.vectorstores import Chroma

logger = logging.getLogger(__name__)

class KnowledgeRetriever:
    def __init__(self, path, suffixes, language):
        logger.debug('Initializing KnowledgeRetriever')
        self.path = path
        logger.debug(f'Path: {self.path}')
        self.loader = KnowledgeLoader(self.path, "**/*", suffixes, language=language)
        self.reload()
        logger.debug('KnowledgeRetriever initialized')

    @classmethod
    def from_documents(cls, path, suffixes, language):
        return cls(path, suffixes, language)

    def reload(self):
        logger.debug('Reloading knowledge')
        # Load the knowledge from the filesystem
        documents = self.loader.load() 
        self.db = Chroma.from_documents(documents,
          OpenAIEmbeddings(disallowed_special=()),
          persist_directory=f"{self.path}/db",
        )

        logger.debug('Knowledge reloaded')

    def as_retriever(self):
        return self.db.as_retriever(
            search_type="mmr",  # Also test "similarity"
            search_kwargs={"k": 8},
        )
