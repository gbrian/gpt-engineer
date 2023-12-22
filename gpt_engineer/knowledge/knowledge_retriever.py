import logging
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader

from gpt_engineer.settings import GPTENG_PATH

from gpt_engineer.knowledge.knowledge_loader import KnowledgeLoader

logger = logging.getLogger(__name__)

class KnowledgeRetriever:
    db_path = f"{GPTENG_PATH}/db"
    db = None

    def __init__(self, path):
        logger.debug(f'Initializing KnowledgeRetriever {path}')
        self.path = path
        self.loader = KnowledgeLoader(self.path)
        self.embedding = OpenAIEmbeddings(disallowed_special=())
        logger.debug('KnowledgeRetriever initialized')

    def get_db(self):
      if not self.db:
        self.db = Chroma(persist_directory=self.db_path, 
                  embedding_function=self.embedding)
      return self.db
    def reload(self):
        logger.debug('Reloading knowledge')
        # Load the knowledge from the filesystem
        documents = self.loader.load() 
        self.db = Chroma.from_documents(documents,
          self.embedding,
          persist_directory=self.db_path,
        )
        logger.debug('Knowledge reloaded')

    def as_retriever(self):
        return self.get_db().as_retriever(
            search_type="mmr",  # Also test "similarity"
            search_kwargs={"k": 8},
        )

    def search(self, query):
      retriever = self.as_retriever()
      return retriever.get_relevant_documents(query)
