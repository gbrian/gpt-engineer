import logging
import pytest
from unittest.mock import patch, MagicMock

from gpt_engineer.core.db import DB
from gpt_engineer.core.dbs import DBs

from gpt_engineer.knowledge.knowledge_prompts import KnowledgePrompts
from gpt_engineer.knowledge.knowledge import Knowledge
from gpt_engineer.knowledge.knowledge_loader import KnowledgeLoader

# Fixture to mock AI and DBs instances

path = "tests/knowledge"
    
@pytest.fixture
def mock_ai_dbs():
    dbs = MagicMock(spec=DBs)
    dbs.preprompts = DB("gpt_engineer/preprompts")
    return dbs

def test_knowledge_loader(mock_ai_dbs):
  loader = KnowledgeLoader(path)

  docs = loader.load()
  languages = [doc.metadata.get('language') for doc in docs]
  loaders = [doc.metadata.get('loader_type') for doc in docs]
  sources = [doc.metadata.get('source') for doc in docs]
  
  assert "python" in languages
  assert "markdown" in languages
  assert "code" in loaders
  assert "text" in loaders
  assert "tests/knowledge/settings.json" in sources
  
def test_knowledge(mock_ai_dbs):
    dbs = mock_ai_dbs
    knowledge_prompts = KnowledgePrompts(dbs.preprompts)
    knowledge = Knowledge(
        path, knowledge_prompts=knowledge_prompts)

    knowledge.reload(full=True)

    docs = knowledge.get_all_documents()
    

    assert docs
    
