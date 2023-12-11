import pytest
import glob
import os

from gpt_engineer.knowledge.knowledge_chat import KnowledgeChat
from gpt_engineer.knowledge.knowledge_loader import KnowledgeLoader
from gpt_engineer.knowledge.knowledge_retriever import KnowledgeRetriever
from gpt_engineer.knowledge.knowledge_splitter import KnowledgeSplitter

@pytest.mark.skip(reason="Temporarily skipping this test")
def test_knowledge_chat():
    chat = KnowledgeChat('llm', KnowledgeRetriever(['This is a test document.'], 'embeddings', 'mmr', {'k': 8}).as_retriever(), 'memory')
    answer = chat.ask_question('What is this document about?')
    assert isinstance(chat, KnowledgeChat)
    assert answer is not None

def test_knowledge_loader():
    repo_path = 'tests/data'
    loader = KnowledgeLoader(repo_path, '**/*.py', ['.py'], 'parser')
    documents = loader.load()
    assert isinstance(loader, KnowledgeLoader)
    assert isinstance(documents, list)
    assert len(documents) == len(glob.glob(os.path.join(repo_path, '**/*.py'), recursive=True))

@pytest.mark.skip(reason="Temporarily skipping this test")
def test_knowledge_retriever():
    retriever = KnowledgeRetriever(['This is a test document.'], 'embeddings', 'mmr', {'k': 8})
    retriever_obj = retriever.as_retriever()
    assert isinstance(retriever, KnowledgeRetriever)
    assert retriever_obj is not None

@pytest.mark.skip(reason="Temporarily skipping this test")
def test_knowledge_splitter():
    splitter = KnowledgeSplitter('python', 2000, 200)
    documents = ['This is a test document.']
    chunks = splitter.split_documents(documents)
    assert isinstance(splitter, KnowledgeSplitter)
    assert isinstance(chunks, list)
    assert len(chunks) > 0
