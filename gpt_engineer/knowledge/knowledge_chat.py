import logging
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory
from langchain.text_splitter import Language
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders.parsers import LanguageParser

from gpt_engineer.settings import MODEL
from gpt_engineer.knowledge.knowledge_retriever import KnowledgeRetriever

logger = logging.getLogger(__name__)

class KnowledgeChat:
    def __init__(self, path, suffixes, language=Language.PYTHON):
        logger.debug('Initializing KnowledgeChat')
        self.path = path
        logger.debug(f'Path: {self.path}')
        self.llm = ChatOpenAI(model_name="gpt-4")
        self.memory = ConversationSummaryMemory(
            llm=self.llm, memory_key="chat_history", return_messages=True
        )
        self.retriever = KnowledgeRetriever.from_documents(self.path, suffixes, language).as_retriever()
        self.qa = ConversationalRetrievalChain.from_llm(self.llm, retriever=self.retriever, memory=self.memory)
        logger.debug('KnowledgeChat initialized')

    @classmethod
    def from_llm(cls, path):
        return cls(path)

    def ask_question(self, question):
        logger.debug(f'Asking question: {question}')
        # Ask a question and get an answer
        result = self.qa(question)
        logger.debug(f'Received answer: {result}')
        return result