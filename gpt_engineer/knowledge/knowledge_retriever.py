import logging
import os
import shutil

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI

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
        last_update = None
        if os.path.exists(self.db_path):
          last_update = os.path.getmtime(self.db_path)
        documents = self.loader.load(last_update=last_update)
        if len(documents):
          if last_update:
            self.delete_old_documents(documents)
          self.db = Chroma.from_documents(documents,
            self.embedding,
            persist_directory=self.db_path,
          )
        logger.debug('Knowledge reloaded')

    def delete_old_documents (self, documents):
      logger.debug('Removing old documents')
      ids_to_delete = []
      collection = self.get_db()._collection
      collection_docs = collection.get(include=['metadatas'])
      def delete_doc_ids (source_doc):
        for ix, metadata in enumerate(collection_docs["metadatas"]):
            if metadata.get('source') == source_doc:
                id_to_delete = collection_docs["ids"][ix]
                logger.debug(f"Document to delete: {id_to_delete}: {source_doc}")
                ids_to_delete.append(id_to_delete)

      sources = list(dict.fromkeys([doc.metadata["source"] for doc in documents]))
      for source in sources:
        delete_doc_ids(source_doc=source)

      logger.debug(f'Documents to delete: {sources} {ids_to_delete}')
      collection.delete(ids=ids_to_delete)

    def reset(self):
        logger.debug('Reseting retriever')
        self.db = None
        if os.path.exists(self.db_path):
            shutil.rmtree(self.db_path)

    def as_retriever(self):
        return self.get_db().as_retriever(
            search_type="mmr",  # Also test "similarity"
            search_kwargs={"k": 8},
        )

    def search(self, query):
      retriever = self.as_retriever()
      return retriever.get_relevant_documents(query)
