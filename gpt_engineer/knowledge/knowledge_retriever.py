from langchain.embeddings.openai import OpenAIEmbeddings
from gpt_engineer.knowledge.knowledge_loader import KnowledgeLoader
from langchain.vectorstores import Chroma

class KnowledgeRetriever:
    def __init__(self, path, suffixes, language):
        self.path = path
        self.loader = KnowledgeLoader(self.path, "**/*", suffixes, language=language)
        self.reload()

    @classmethod
    def from_documents(cls, path, suffixes, language):
        return cls(path, suffixes, language)
        
    def reload(self):
        # Load the knowledge from the filesystem
        documents = self.loader.load() 
        self.db = Chroma.from_documents(documents,
          OpenAIEmbeddings(disallowed_special=()),
          persist_directory=self.path)

    def as_retriever(self):
        return self.db.as_retriever(
            search_type="mmr",  # Also test "similarity"
            search_kwargs={"k": 8},
        )
