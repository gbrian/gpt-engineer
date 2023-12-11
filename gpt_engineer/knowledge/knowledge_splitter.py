class KnowledgeSplitter:
    def __init__(self, language, chunk_size, chunk_overlap):
        self.language = language
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @classmethod
    def from_language(cls, language, chunk_size, chunk_overlap):
        return cls(language, chunk_size, chunk_overlap)

    def split_documents(self, documents):
        # Split the documents into chunks
        pass