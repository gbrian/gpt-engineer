import pytest
import glob
import os

from langchain.schema.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import Language

from gpt_engineer.knowledge.knowledge_chat import KnowledgeChat
from gpt_engineer.knowledge.knowledge_loader import KnowledgeLoader
from gpt_engineer.knowledge.knowledge_retriever import KnowledgeRetriever
from gpt_engineer.knowledge.knowledge_splitter import KnowledgeSplitter

TEST_DOCUMENT = Document(page_content="This is a test document.", metadata={"source": "local"})

def test_knowledge_chat():
    chat = KnowledgeChat('tests/data', suffixes=['.py'], language=Language.PYTHON)
    answer = chat.ask_question('What is this document about?')
    assert isinstance(chat, KnowledgeChat)
    assert answer is not None

def test_knowledge_loader():
    repo_path = 'tests/data'
    parser = 'parser'
    loader = KnowledgeLoader(repo_path, '**/*.py', ['.py'], parser)
    documents = loader.load()
    assert isinstance(loader, KnowledgeLoader)
    assert isinstance(documents, list)
    assert len(documents) == len(glob.glob(os.path.join(repo_path, '**/*.py'), recursive=True))

def test_knowledge_retriever():
    db = Chroma.from_documents([TEST_DOCUMENT], OpenAIEmbeddings(disallowed_special=()))
    assert isinstance(db, Chroma)
    retriever = db.as_retriever(search_type="mmr", search_kwargs={"k": 8})
    assert retriever is not None

def test_knowledge_splitter():
    splitter = KnowledgeSplitter('python', 2000, 200)
    documents = [TEST_DOCUMENT]
    chunks = splitter.split_documents(documents)
    assert isinstance(splitter, KnowledgeSplitter)
    assert isinstance(chunks, list)
    assert len(chunks) > 0
