from langchain.text_splitter import RecursiveCharacterTextSplitter, Language

class KnowledgeSplitter:
    def __init__(self, language, chunk_size, chunk_overlap):
        self.language = language
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @classmethod
    def from_language(cls, language, chunk_size, chunk_overlap):
        return cls(language, chunk_size, chunk_overlap)

    def split_documents(self, documents):
        python_splitter = RecursiveCharacterTextSplitter.from_language(
          language=Language.PYTHON, chunk_size=2000, chunk_overlap=200
        )
        chunks = python_splitter.split_documents(documents)
        return chunks