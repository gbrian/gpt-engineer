from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory
from langchain.text_splitter import Language
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders.parsers import LanguageParser

from gpt_engineer.settings import MODEL
from gpt_engineer.knowledge.knowledge_loader import KnowledgeLoader
from gpt_engineer.knowledge.knowledge_retriever import KnowledgeRetriever

class KnowledgeChat:
    def __init__(self, repo_path, suffixes, language=Language.PYTHON):
        self.llm = ChatOpenAI(model_name="gpt-4")
        self.loader = KnowledgeLoader(repo_path, "**/*", suffixes, language=language)
        self.memory = ConversationSummaryMemory(
            llm=self.llm, memory_key="chat_history", return_messages=True
        )
        self.retriever = self.reload()
        self.qa = ConversationalRetrievalChain.from_llm(self.llm, retriever=self.retriever, memory=self.memory)

    @classmethod
    def from_llm(cls, repo_path):
        return cls(repo_path)

    def reload(self):
        # Load the knowledge from the filesystem
        documents = self.loader.load()
        # Create a new KnowledgeRetriever with these documents
        retriever = KnowledgeRetriever.from_documents(documents)
        return retriever.as_retriever()

    def ask_question(self, question):
        # Ask a question and get an answer
        result = self.qa(question)
        return result