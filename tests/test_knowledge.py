import pytest
import glob
import os

from langchain.schema.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import Language

from gpt_engineer.knowledge.knowledge_search import KnowledgeSearch
from gpt_engineer.knowledge.knowledge_loader import KnowledgeLoader
from gpt_engineer.knowledge.knowledge_retriever import KnowledgeRetriever
from gpt_engineer.knowledge.knowledge_splitter import KnowledgeSplitter

TEST_DOCUMENT = Document(page_content="This is a test document.", metadata={"source": "local"})

def test_knowledge_search_ai_class():
    chat = KnowledgeSearch('tests/data', suffixes=['.py'], language=Language.PYTHON, ids=['test_id'])
    question = "What is the purpose of the AI class in the ai.py file?"
    expected_answer = "ai.py\nThe AI class provides an interface to interact with a language model for chat-based interactions. It handles token counting, message creation, serialization and deserialization of chat messages, and interfaces with the language model to get AI-generated responses."
    answer = chat.ask_question(question)
    assert answer == expected_answer

def test_knowledge_search_parse_chat_function():
    chat = KnowledgeSearch('tests/data', suffixes=['.py'], language=Language.PYTHON, ids=['test_id'])
    question = "What does the parse_chat function do in the chat_to_files.py file?"
    expected_answer = "chat_to_files.py\nThe parse_chat function extracts all code blocks from a chat and returns them as a list of (filename, codeblock) tuples."
    answer = chat.ask_question(question)
    assert answer == expected_answer

def test_knowledge_search_db_class():
    chat = KnowledgeSearch('tests/data', suffixes=['.py'], language=Language.PYTHON, ids=['test_id'])
    question = "What is the DB class in the db.py file used for?"
    expected_answer = "db.py\nThe DB class represents a simple database that stores its data as files in a directory. It provides an interface to a file-based database, leveraging file operations to facilitate CRUD-like interactions."
    answer = chat.ask_question(question)
    assert answer == expected_answer

def test_knowledge_search_to_files_and_memory_function():
    chat = KnowledgeSearch('tests/data', suffixes=['.py'], language=Language.PYTHON, ids=['test_id'])
    question = "What does the to_files_and_memory function do in the chat_to_files.py file?"
    expected_answer = "chat_to_files.py\nThe to_files_and_memory function saves chat to memory, and parses chat to extracted file and saves them to the workspace."
    answer = chat.ask_question(question)
    assert answer == expected_answer

def test_knowledge_search_archive_function():
    chat = KnowledgeSearch('tests/data', suffixes=['.py'], language=Language.PYTHON, ids=['test_id'])
    question = "What does the archive function do in the db.py file?"
    expected_answer = "db.py\nThe archive function archives the memory and workspace databases."
    answer = chat.ask_question(question)
    assert answer == expected_answer

def test_knowledge_loader():
    path = 'tests/data'
    parser = 'parser'
    loader = KnowledgeLoader(path, '**/*.py', ['.py'], parser)
    documents = loader.load()
    assert isinstance(loader, KnowledgeLoader)
    assert isinstance(documents, list)
    assert len(documents) == len(glob.glob(os.path.join(path, '**/*.py'), recursive=True))

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
