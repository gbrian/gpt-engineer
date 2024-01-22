import logging
import pytest
from unittest.mock import patch, MagicMock

from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DB, DBs
from gpt_engineer.core.steps import ai_validate_context, parallel_validate_contexts
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

VALIDATE_DATA = [
  ("Tell me about python", "Python is a coding language", 1),
  ("Update the step validator function", '''
  def select_files_from_knowledge(ai: AI, dbs: DBs):
    query = dbs.input[PROMPT_FILE]
    documents = dbs.knowledge.search(query)
    dbs.input.append(
      HISTORY_PROMPT_FILE, f"\n[[KNOWLEDGE]]\n{documents}"
    )
    if documents:
        # Filter out irrelevant documents based on a relevance score
        relevant_documents = [doc for doc in parallel_validate_contexts(dbs, query, documents) if doc]
        file_list = [str(Path(doc.metadata["source"]).absolute()) for doc in relevant_documents]
        file_list = list(dict.fromkeys(file_list))  # Remove duplicates

        print(f"{len(file_list)} matches using knowledge:")
        for i, path in enumerate(file_list):
            print(f"{i + 1}. {path}")

        user_input = input(
          "Select files by entering the numbers separated by commas/spaces or specify range with a dash.\n"
          + "Example: 1,2,3-5,7,9,13-15,18,20 or enter 'all' to select everything.\n"
          + "Select files (default: all): ")

  ''', 1)
]


def test_validate_context(mock_ai_dbs):
  ai, dbs = mock_ai_dbs
  
  for \
  prompt, page_content, expected_score in VALIDATE_DATA: 
    metadata={}
    doc = Document(id=None, page_content=page_content, metadata=metadata)
    res = ai_validate_context(ai, dbs, prompt, doc, retry_count=1)

    assert res is not None
    assert float(res.metadata["relevance_score"]) == expected_score
