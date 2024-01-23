TEST_DATA = [
  ('''I would rate the relevance of this code to the given task as SCORE: 0.2. gpt_engineer" API app instead of the normal''',
    0.2),
  ('''Based on the provided information, the relevance of the given file path and code to the task 
  of adding the "--api" option to the CLI and running the "gpt_engineer" API app instead of the normal flow is low.
  The provided code does not include any logic related to the "--api" option or running the API app. Therefore, the 
  score for relevance would be low, around SCORE: 0.2.''',
    0.2),
  ('''The relevance of this code depends on the specific task or project you are working on.
  If you are using the `gpt-engineer` library and need to integrate it with open-source models or Azure models,
  then this code is highly relevant as it provides instructions on how to do so. However, if you are not using the
  `gpt-engineer` library or do not need to integrate it with these models, then this code may not be relevant to your current task.''',
    None),
  ('''The relevance of the given file path and code snippet to the task of adding the "--api" option to the CLI for running 
  the "gpt_engineer" API app instead of the normal flow is low. The provided code is a docker-compose file that defines a service and 
  its configuration, but it does not directly relate to the task at hand.''',
    None),
  ('''The relevance of the given file path and code snippet to the task of adding the "--api" option to the CLI for running 
  the "gpt_engineer" API app instead of the normal flow is low. The provided code is a docker-compose file that defines a service and 
  its configuration, but it does not directly relate to the task at hand. 1.2.3.4''',
    None),
  ('''The relevance of the provided code to the task of adding the "--api" option to the CLI to run the gpt_engineer 
  API app instead of the normal flow is low. The code is a disclaimer for the gpt-engineer application and does not provide 
  any information or instructions on how to add the "--api" option to the CLI.

  Therefore, the score for relevance in this case would be low, around 0.2.''',
    None),
  ('''Based on the provided code, the relevance of adding the "--api" option to the CLI tool to run the gpt_engineer API app instead of the normal flow would be:

  SCORE: 0.7''',
    0.7),
  ('''SCORE: 0.6''',
    0.6)
]

import pytest
from unittest.mock import patch, MagicMock

from gpt_engineer.core.context import get_response_score


# Fixture to mock AI and DBs instances
@pytest.fixture
def mock_ai_dbs():
    ai = MagicMock(spec=AI)
    dbs = MagicMock(spec=DBs)
    return ai, dbs

def test_get_response_score():
    for doc, expected_score in TEST_DATA:
      score = get_response_score(doc)
      assert expected_score == score