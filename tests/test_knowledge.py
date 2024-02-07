import logging
import pytest
from unittest.mock import patch, MagicMock

from gpt_engineer.core.db import DB
from gpt_engineer.core.dbs import DBs

from gpt_engineer.knowledge.knowledge_prompts import KnowledgePrompts
from gpt_engineer.knowledge.knowledge import Knowledge

# Fixture to mock AI and DBs instances

path = "tests/knowledge"
    
@pytest.fixture
def mock_ai_dbs():
    dbs = MagicMock(spec=DBs)
    dbs.preprompts = DB("gpt_engineer/preprompts")
    return dbs
  
def test_knowledge_code_indexing(mock_ai_dbs):
    dbs = mock_ai_dbs
    knowledge_prompts = KnowledgePrompts(dbs.preprompts)
    knowledge = Knowledge(
        path, knowledge_prompts=knowledge_prompts)

    knowledge.reload(full=True)

    docs = knowledge.get_all_documents()

    assert any(doc.page_content == 'class DummyPython:\n    def dummy_method(self):\n        pass\n' for doc in docs)
    assert any(doc.page_content == 'class DummyTypeScript {\n    dummyMethod() {}\n}\n' for doc in docs)
    assert any(doc.page_content == 'class DummyJavaScript {\n    dummyMethod() {}\n}\n' for doc in docs)
    assert any(doc.page_content == 'public class DummyJava {\n    public void dummyMethod() {}\n}\n' for doc in docs)
    
