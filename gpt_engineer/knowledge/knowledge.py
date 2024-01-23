import logging
import os
import shutil
from slugify import slugify
from datetime import datetime

from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.schema.document import Document

from gpt_engineer.core.ai import AI
from gpt_engineer.settings import GPTENG_PATH, KNOWLEDGE_MODEL, ENRICH_DOCUMENTS

from gpt_engineer.knowledge.knowledge_loader import KnowledgeLoader

logger = logging.getLogger(__name__)

class DBDocument (Document):
  db_id: str = None
  def __init__(self, id, metadata, page_content=""):
    Document.__init__(self, id=id, page_content=page_content, metadata=metadata)
    self.db_id = id

class Knowledge:
    db_path: str
    db_file_list: str
    index_name: str
    db: Chroma = None

    def __init__(self, path: str, enrich_prompt: str = None):
        logger.debug(f'Initializing Knowledge {path}')
        
        self.ai = AI(model_name=KNOWLEDGE_MODEL)

        self.path = path
        self.enrich_prompt = enrich_prompt
        self.index_name = slugify(str(path))
        self.db_path = f"{GPTENG_PATH}/db/{self.index_name}"
        self.db_file_list = f"{self.db_path}/file_list"

        self.loader = KnowledgeLoader(self.path)
        self.embedding = OpenAIEmbeddings(disallowed_special=())
        self.last_update = None
        
        if os.path.isfile(self.db_file_list):
          self.last_update = os.path.getmtime(self.db_file_list)
        self.last_changed_file_paths = []
        logger.debug('Knowledge initialized')
    
    def get_db(self):
      if not self.db:
        self.db = Chroma(persist_directory=self.db_path, 
                  embedding_function=self.embedding)
      return self.db

    def reload(self, full: bool = False):
        if full:
          self.reset()

        logger.debug('Reloading knowledge')
        # Load the knowledge from the filesystem
        documents = self.loader.load(last_update=self.last_update)
        if documents:
          self.index_documents(documents)
          self.last_changed_file_paths = list(dict.fromkeys([d.metadata["source"] for d in documents]))
          self.build_summary()
          logger.debug('Knowledge reloaded')
        changes = self.clean_deleted_documents()
        if changes or documents: 
          self.build_summary()
        return True if len(documents) else False

    def get_all_documents (self, include=[]):
        logger.debug('Get all documents')
        collection = self.get_db()._collection
        collection_docs = collection.get(include=include + ['metadatas'])
        documents = []
        ids = collection_docs["ids"]
        metadatas = collection_docs["metadatas"]
        page_contents = collection_docs.get("documents", [])
        for ix, _id in enumerate(ids):
          page_content = ""
          if page_contents:
            page_content = page_contents[ix]
          documents.append(DBDocument(id=_id, page_content=page_content, metadata=metadatas[ix]))
        return documents

    def get_all_sources (self):
        documents = self.get_all_documents()
        doc_sources = list(dict.fromkeys([doc.metadata["source"] for doc in documents]))
        logger.debug(f'All sources {len(doc_sources)}')        
        return doc_sources
        
    def clean_deleted_documents(self):
        logger.debug('Removing deleted documents')
        ids_to_delete = []
        collection = self.get_db()._collection
        documents = self.get_all_documents()
        
        sources = []
        for doc in documents:
          source = doc.metadata["source"]
          if not os.path.isfile(source):
            sources.append(source)
            ids_to_delete.append(doc.db_id)

        if len(ids_to_delete):
          logger.debug(f'Documents to delete: {sources} {ids_to_delete}')
          collection.delete(ids=ids_to_delete)
          return True
        return False

    def enrich_document (self, doc, metadata):
      if doc.metadata.get("indexed"):
        raise Exception(f"Doc already indexed {doc.metadata}")
      for k in metadata.keys():
        doc.metadata[k] = metadata[k]
      language = doc.metadata.get('language', '')
      source = doc.metadata.get('source')
      response = ""
      if ENRICH_DOCUMENTS:
        try:
          prompt = doc.page_content
          if self.enrich_prompt:
            prompt = self.enrich_prompt.replace("{{ page_content }}", prompt) \
                                      .replace("{{ language }}", language)
          system = "" # Do we need it?
          messages = self.ai.start(system, prompt, step_name="enrich_document")
          response = messages[-1].content.strip()
        except Exception as ex:
          logger.debug(f"Error enriching document {source}: {ex}")
          pass
      doc.page_content = "\n".join([
          f"File path: {source}",
          f"Summary: {response}",
          "Code:"
          f"```{language}",
          doc.page_content,
          "```"
      ])
      doc.metadata["indexed"] = 1
      return doc

    def parallel_enrich(self, documents, metadata):
      with ThreadPoolExecutor() as executor:
        futures = {
          executor.submit(
            self.enrich_document,
            doc=doc,
            metadata=metadata): doc for doc in documents
        }
        valid_documents = []
        for future in as_completed(futures):
          result = future.result()
          if result is not None:
              valid_documents.append(result)
        return valid_documents
  
    def index_documents (self, documents):
        if self.last_update:
          self.delete_old_documents(documents)
        index_date = datetime.now().strftime("%m/%d/%YT%H:%M:%S")
        metadata = {
          "index_date": f"{index_date}"
        }
        documents = self.parallel_enrich(documents, metadata=metadata)
        self.db = Chroma.from_documents(documents,
          self.embedding,
          persist_directory=self.db_path,
        )

    def get_last_changed_file_paths (self):
      return self.last_changed_file_paths

    def build_summary(self):
        try:
          os.mkdir(self.db_path, exist_ok=True)
        except:
          pass
        current_files = [f"{doc.metadata['source']} {doc.metadata.get('language')}" for doc in self.get_all_documents()]
        db_files = list(dict.fromkeys(current_files))
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
      documents = retriever.get_relevant_documents(query)
      logging.debug(f"[Knowledge::search] {query} docs: {len(documents)}")
      return documents

    def index_document(self, text, metadata):
        documents = [Document(page_content=text, metadata=metadata)]
        self.delete_old_documents(documents)
        self.index_documents(documents)
