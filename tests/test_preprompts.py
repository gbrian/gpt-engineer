import logging
import pytest
from unittest.mock import patch, MagicMock

from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DB, DBs
from gpt_engineer.core.context import ai_validate_context, parallel_validate_contexts
from langchain.schema.document import Document

from gpt_engineer.settings import KNOWLEDGE_MODEL

# Fixture to mock AI and DBs instances
@pytest.fixture
def mock_ai_dbs():
    ai = AI(model_name=KNOWLEDGE_MODEL)
    dbs = MagicMock(spec=DBs)
    dbs.roles = DB("gpt_engineer/preprompts/roles")
    dbs.preprompts = DB("gpt_engineer/preprompts")
    return ai, dbs

