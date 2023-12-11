from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory
from langchain.text_splitter import Language
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders.parsers import LanguageParser

from gpt_engineer.settings import MODEL
from gpt_engineer.knowledge.knowledge_retriever import KnowledgeRetriever

class KnowledgeChat:
    def __init__(self, path, suffixes, language=Language.PYTHON):
        self.path = path
        self.llm = ChatOpenAI(model_name="gpt-4")
        self.memory = ConversationSummaryMemory(
            llm=self.llm, memory_key="chat_history", return_messages=True
        )
        self.retriever = KnowledgeRetriever.from_documents(self.path, suffixes, language).as_retriever()
        self.qa = ConversationalRetrievalChain.from_llm(self.llm, retriever=self.retriever, memory=self.memory)

    @classmethod
    def from_llm(cls, path):
        return cls(path)

    def ask_question(self, question):
        # Ask a question and get an answer
        result = self.qa(question)
        return result