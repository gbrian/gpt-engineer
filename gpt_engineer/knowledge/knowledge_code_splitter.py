import logging

from langchain.schema.document import Document
from langchain.text_splitter import Language
from langchain.document_loaders.parsers import LanguageParser
from langchain_community.document_loaders.blob_loaders import Blob

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter

from llama_index.core.node_parser import CodeSplitter
from gpt_engineer.settings import (
    LANGUAGE_FROM_EXTENSION
)

CURRENT_SPLITTER_LANGUAGES = [lang.lower() for lang in dir(Language)]
LANGUAGE_PARSER_MAPPING = {
    "ts": "js"
}

class KnowledgeCodeSplitter:
    def __init__(self):
        self.text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=500, chunk_overlap=0
        )

    def load(self, file_path):
        try:
            return self.load_with_code_plitter(file_path=file_path)
        except Exception as ex:
            logging.debug(f"[KnowledgeCodeSplitter] load_with_code_plitter load error: {ex} - {file_path}")

        try:
            return self.load_with_language_parser(file_path=file_path)
        except Exception as ex:
            logging.debug(f"[KnowledgeCodeSplitter] load_with_language_parser load error: {ex} - {file_path}")
            
        try:
            return self.load_as_text(file_path=file_path)
        except Exception as ex:
            logging.debug(f"[KnowledgeCodeSplitter] load_as_text load error: {ex} - {file_path}")

        return None

    def load_with_code_plitter(self, file_path):
        suffix = file_path.split(".")[-1] if "." in file_path else "txt"
        language = LANGUAGE_FROM_EXTENSION.get(suffix)
        code_parser = CodeSplitter(
            language=language,
            # chunk_lines: int = DEFAULT_CHUNK_LINES,
            # chunk_lines_overlap: int = DEFAULT_LINES_OVERLAP,
            # max_chars: int = DEFAULT_MAX_CHARS,
            # parser: Any = None,
            # callback_manager: Optional[CallbackManager] = None,
            # include_metadata: bool = True,
            # include_prev_next_rel: bool = True,
            # id_func: Optional[Callable[[int, Document], str]] = None,
        )
        def build_document(page_content):
            metadata = {
                "source": file_path,
                "language": language,
                "parser": "CodeSplitter",
                "loader_type": "code"
            }    
            return Document(page_content=page_content, metadata=metadata)

        with open(file_path, mode='r', encoding='utf-8') as file:
            blocks = code_parser.split_text(file.read())
            return [build_document(block) for block in blocks]

    def load_with_language_parser(self, file_path):
        suffix = file_path.split(".")[-1] if "." in file_path else "txt"
        
        language = LANGUAGE_FROM_EXTENSION.get(suffix)
        language_parser_language = LANGUAGE_PARSER_MAPPING.get(language) or language
        language_parser = LanguageParser(language=language_parser_language)
        with open(file_path, mode='r', encoding='utf-8') as file:
            blob = Blob(data=file.read(), encoding='utf-8', metadata={ 
                "source": file_path,
                "language": language,
                "parser": "LanguageParser"
            })
            docs = language_parser.parse(blob)
            for doc in docs: # Dirty hack for json
                doc.metadata["language"] = doc.metadata.get("language") or language or suffix
                doc.metadata["loader_type"] = "code"
            return docs

    def load_as_text(self, file_path):
      docs = TextLoader(file_path).load_and_split(
                    text_splitter=self.text_splitter)
      for doc in docs:
          doc.metadata["language"] = "txt"
          doc.metadata["loader_type"] = "text"
      return docs
      