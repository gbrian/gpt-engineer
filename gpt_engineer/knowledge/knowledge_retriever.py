import logging
import os
import shutil
from datetime import datetime

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.schema.document import Document

from gpt_engineer.settings import GPTENG_PATH

from gpt_engineer.knowledge.knowledge_loader import KnowledgeLoader

logger = logging.getLogger(__name__)

class KnowledgeRetriever:
    db_path = f"{GPTENG_PATH}/db"
    db_file_list = f"{GPTENG_PATH}/db/file_list"
    db = None

    def __init__(self, path):
        logger.debug(f'Initializing KnowledgeRetriever {path}')
        self.path = path
        self.loader = KnowledgeLoader(self.path)
        self.embedding = OpenAIEmbeddings(disallowed_special=())
        self.last_update = None
        if os.path.isfile(self.db_file_list):
          self.last_update = os.path.getmtime(self.db_file_list)
        self.last_changed_file_paths = []
        logger.debug('KnowledgeRetriever initialized')

    def get_db(self):
      if not self.db:
        self.db = Chroma(persist_directory=self.db_path, 
                  embedding_function=self.embedding)
      return self.db

    def reload(self):
        logger.debug('Reloading knowledge')
        # Load the knowledge from the filesystem
        documents = self.loader.load(last_update=self.last_update)
        if len(documents):
          self.index_documents(documents)
          self.last_changed_file_paths = list(dict.fromkeys([d.metadata["source"] for d in documents]))
          self.build_summary()
          logger.debug('Knowledge reloaded')
        return True if len(documents) else False

    def enrich_document (self, doc, metadata):
      if doc.metadata.get("indexed"):
        raise Exception(f"Doc already indexed {doc.metadata}")
      for k in metadata.keys():
        doc.metadata[k] = metadata[k]
      doc.page_content = f"DOCUMENT METADATA:\n{doc.metadata}\nDOCUMENT CONTENT:\n{doc.page_content}"
      doc.metadata["indexed"] = 1
      return doc
  
    def index_documents (self, documents):
        if self.last_update:
          self.delete_old_documents(documents)
        index_date = datetime.now().strftime("%m/%d/%YT%H:%M:%S")
        metadata = {
          "index_date": f"{index_date}"
        }
        for doc in documents:
          doc = self.enrich_document(doc, metadata)
        self.db = Chroma.from_documents(documents,
          self.embedding,
          persist_directory=self.db_path,
        )

    def get_db_files (self):
      # Read current files
      if os.path.isfile(self.db_file_list):
        with open(self.db_file_list, "r") as db_files: 
          return db_files.read().split("\n")
      return []

    def get_last_changed_file_paths (self):
      return self.last_changed_file_paths

    def build_summary(self):
        try:
          os.mkdir(self.db_path, exist_ok=True)
        except:
          pass
        current_files = self.get_db_files()
        db_files = list(dict.fromkeys(self.last_changed_file_paths + current_files))
        # Save all files
        with open(self.db_file_list, "w") as db_file_list:
          db_file_list.write("\n".join(db_files))
        

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

        if len(ids_to_delete):
          logger.debug(f'Documents to delete: {sources} {ids_to_delete}')
          collection.delete(ids=ids_to_delete)

    def reset(self):
        logger.debug('Reseting retriever')
        self.db = None
        self.last_update = None
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

    def index_document(self, text, metadata):
        documents = [Document(page_content=text, metadata=metadata)]
        self.delete_old_documents(documents)
        self.index_documents(documents)
