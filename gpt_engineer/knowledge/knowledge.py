import logging
import os
import shutil
from slugify import slugify
from datetime import datetime
from functools import reduce
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import OpenAI
from langchain.schema.document import Document

from gpt_engineer.core.ai import AI
from gpt_engineer.core.settings import GPTEngineerSettings
from gpt_engineer.knowledge.knowledge_loader import KnowledgeLoader
from gpt_engineer.knowledge.knowledge_prompts import KnowledgePrompts

logger = logging.getLogger(__name__)

def make_tag (tag):
  return f"TAG_{tag.replace(' ', '_')}"

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

    def __init__(self, settings: GPTEngineerSettings, knowledge_prompts: KnowledgePrompts = None):
        self.settings = settings

        self.path = self.settings.project_path
        self.knowledge_prompts = knowledge_prompts
        self.index_name = slugify(str(self.path))
        self.db_path = f"{settings.gpteng_path}/db/{self.index_name}"
        self.db_file = f"{self.db_path}/chroma.sqlite3"
        self.db_file_list = f"{self.db_path}/file_list"

        self.loader = KnowledgeLoader(settings=settings)
        self.embedding = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_api_base,
            disallowed_special=()
        )
        self.last_update = None
        self.refresh_last_update()        
        self.last_changed_file_paths = []

    def get_ai(self):
      from gpt_engineer.core import build_ai
      if not self.ai:
        self.ai = build_ai(settings=self.settings)
      return self.ai

    def get_db(self):
      if not self.db:
        self.db = Chroma(persist_directory=self.db_path, 
                  embedding_function=self.embedding)
      return self.db

    def refresh_last_update(self):
      if os.path.isfile(self.db_file):
          self.last_update = os.path.getmtime(self.db_file)

    def detect_changes(self):
      current_sources = self.get_all_sources()
      changes = self.loader.list_repository_files(last_update=self.last_update if current_sources else None,
                          current_sources=current_sources)
      return changes

    def reload(self, full: bool = False):
        if not self.settings.use_knowledge:
            return
        self.refresh_last_update()
        if full:
          self.reset()
        try:
            logger.info('Reloading knowledge')
            # Load the knowledge from the filesystem
            current_sources = self.get_all_sources()
            documents = self.loader.load(last_update=self.last_update if current_sources else None,
                                current_sources=current_sources)
            if documents:
                self.index_documents(documents)

            self.last_changed_file_paths = list(dict.fromkeys([d.metadata["source"] for d in documents]))
            self.build_summary()
            logger.info('Knowledge reloaded')
            changes = self.clean_deleted_documents()
            if changes or documents: 
                self.build_summary()
            return True if len(documents) else False
        except Exception as ex:
            logger.error(f"Error loading knowledge {ex}")
            pass
        self.refresh_last_update()

    def reload_path(self, path: str):
        logging.info(f"reload_path {path}")
        try:
            documents = self.loader.load(last_update=None, path=path)
            logging.info(f"reload_path {path} {len(documents)} documents")
            if documents:
                self.index_documents(documents)
            return documents
        except Exception as ex:
            logger.error(f"Error loading knowledge {ex}")
            pass

    def get_all_documents (self, include=[]):
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
        
    def clean_deleted_documents(self):
        ids_to_delete = []
        collection = self.get_db()._collection
        documents = self.get_all_documents()
        
        sources = []
        for doc in documents:
          source = doc.metadata["source"]
          if not self.loader.is_valid_file(source):
            sources.append(source)
            ids_to_delete.append(doc.db_id)

        if len(ids_to_delete):
          logger.info(f'Documents to delete: {sources} {ids_to_delete}')
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
      summary = ""

      if self.settings.knowledge_enrich_documents:
        try:
          prompt, system = self.knowledge_prompts.enrich_document_prompt(doc)
          messages = self.get_ai().start(system, prompt, step_name="enrich_document")
          summary = messages[-1].content.strip()
        except Exception as ex:
          logger.info(f"Error enriching document {source}: {ex}")
          pass
      if self.settings.knowledge_extract_document_tags:
        try:
          prompt, system = self.knowledge_prompts.extract_document_tags(doc)
          messages = self.get_ai().start(system, prompt, step_name="extract_document_tags")
          response = messages[-1].content.strip()
          keywords = [make_tag(k) for k in response.split(",")]
          doc.metadata["keywords"] = ", ".join(keywords)
        except Exception as ex:
          logger.info(f"Error extracting document keywords {source}: {ex}")
          pass
       
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
        self.delete_documents(documents)
        index_date = datetime.now().strftime("%m/%d/%YT%H:%M:%S")
        metadata = {
          "index_date": f"{index_date}"
        }
        CHUNK_SIZE = 10
        for doc_chunk in [documents[i:i+CHUNK_SIZE] for i in range(len(documents))[::CHUNK_SIZE]]:
          enriched_docs = self.parallel_enrich(doc_chunk, metadata=metadata)
          for enriched_doc in enriched_docs:
            try:
                self.db = Chroma.from_documents([enriched_doc],
                  self.embedding,
                  persist_directory=self.db_path,
                )
                logger.info(f"Stored document from {enriched_doc.metadata['source']}")
            except Exception as ex:
                logger.error(f"Error indexing document {enriched_doc.metadata['source']}: {ex}")

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
        

    def delete_documents (self, documents=None, sources=None):
        logger.info('Removing old documents')
        ids_to_delete = []
        collection = self.get_db()._collection
        collection_docs = collection.get(include=['metadatas'])
        
        def delete_doc_ids (source_doc):
          for ix, metadata in enumerate(collection_docs["metadatas"]):
              if metadata.get('source') == source_doc:
                  id_to_delete = collection_docs["ids"][ix]
                  logger.info(f"Document to delete: {id_to_delete}: {source_doc}")
                  ids_to_delete.append(id_to_delete)
        if not sources:
          sources = list(dict.fromkeys([doc.metadata["source"] for doc in documents]))
        for source in sources:
          delete_doc_ids(source_doc=source)

        if len(ids_to_delete):
          logger.info(f'Documents to delete: {sources} {ids_to_delete}')
          collection.delete(ids=ids_to_delete)

    def reset(self):
        logger.info('Reseting retriever')
        self.db = None
        self.last_update = None
        if os.path.exists(self.db_path):
            shutil.rmtree(self.db_path)

    def as_retriever(self):
        return self.get_db().as_retriever(
            search_type=self.settings.knowledge_search_type,
            search_kwargs={"k": int(self.settings.knowledge_search_document_count) },
        )

    def search(self, query):
      if not self.settings.use_knowledge:
        return []
      if self.settings.knowledge_extract_document_tags:
        keywords = self.extract_query_keywords(query)
        query = f"{query}\n{[make_tag(k) for k in keywords]}"

      retriever = self.as_retriever()
      documents = retriever.get_relevant_documents(query)
      logging.debug(f"[Knowledge::search] {query} docs: {len(documents)}")
      return documents

    def search_in_source(self, query):
      collection = self.get_db()._collection
      collection_docs = collection.get(include=['metadatas', 'documents'])      
      ids = collection_docs["ids"]
      metadatas = collection_docs["metadatas"]
      page_contents = collection_docs.get("documents", [])

      documents = []
      for ix, _id in enumerate(ids):
        if query in metadatas[ix]["source"]:
          documents.append(Document(id=ids[ix], page_content=page_contents[ix], metadata=metadatas[ix]))
      
      return documents

    def extract_query_keywords(self, query):
      try:
        prompt, system = self.knowledge_prompts.extract_query_tags(query)
        messages = self.get_ai().start(system, prompt, step_name="extract_query_tags")
        response = messages[-1].content.strip()
        keywords = [f"TAG_{k}" for k in response.split(",")]
        return keywords
      except Exception as ex:
        logger.info(f"Error extracting document keywords {source}: {ex}")

    def index_document(self, text, metadata):
        documents = [Document(page_content=text, metadata=metadata)]
        self.delete_documents(documents)
        self.index_documents(documents)

    def get_all_sources (self):
        collection = self.get_db()._collection
        collection_docs = collection.get(include=['metadatas'])
        
        metadatas = collection_docs["metadatas"]
        doc_sources = list(dict.fromkeys([metadata["source"] for metadata in metadatas]))
        return doc_sources

    def status (self):
        collection = self.get_db()._collection
        collection_docs = collection.get(include=['metadatas', 'documents'])
        
        ids = collection_docs["ids"]
        metadatas = collection_docs["metadatas"]
        documents = collection_docs["documents"]

        doc_count = len(ids)
        doc_sources = list(dict.fromkeys([metadata["source"] for metadata in metadatas]))


        folders = list(dict.fromkeys([Path(file_path).parent for file_path in doc_sources]))      
        
        file_count = len(doc_sources)
        return {
          "doc_count": doc_count,
          "file_count": file_count,
          "folders": folders,
          "empty": len(documents) - len(metadatas)
        }