from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

class KnowledgeRetriever:
    def __init__(self, documents):
        self.db = Chroma.from_documents(documents,
          OpenAIEmbeddings(disallowed_special=()))

    @classmethod
    def from_documents(cls, documents):
        return cls(documents)

    def as_retriever(self):
        return self.db.as_retriever(
            search_type="mmr",  # Also test "similarity"
            search_kwargs={"k": 8},
        )
