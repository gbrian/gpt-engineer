"""
Test suite for the prompt.py module.

This test suite is designed to ensure that all functions in the prompt.py module
are working as expected, including edge cases.
"""

import pytest
from unittest.mock import patch, MagicMock
from gpt_engineer.core.step.prompt import get_prompt, improve_prompt_with_summary, improve_prompt_with_knowledge, get_improve_prompt
from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DBs

# Fixture to mock AI and DBs instances
@pytest.fixture
def mock_ai_dbs():
    ai = MagicMock(spec=AI)
    dbs = MagicMock(spec=DBs)
    return ai, dbs

# Test get_prompt function when there is no current prompt
def test_get_prompt_no_current_prompt(mock_ai_dbs):
    ai, dbs = mock_ai_dbs
    dbs.input.get.return_value = None
    with patch('builtins.input', return_value='New prompt'):
        assert get_prompt(ai, dbs) == 'New prompt'

# Test get_prompt function when there is a current prompt and user wants to change it
def test_get_prompt_with_current_prompt_change(mock_ai_dbs):
    ai, dbs = mock_ai_dbs
    dbs.input.get.return_value = 'Current prompt'
    with patch('builtins.input', return_value='Changed prompt'):
        assert get_prompt(ai, dbs) == 'Changed prompt'

# Test get_prompt function when there is a current prompt and user wants to keep it
def test_get_prompt_with_current_prompt_keep(mock_ai_dbs):
    ai, dbs = mock_ai_dbs
    dbs.input.get.return_value = 'Current prompt'
    with patch('builtins.input', return_value=''):
        assert get_prompt(ai, dbs) == 'Current prompt'

# Test improve_prompt_with_knowledge function
def test_improve_prompt_with_knowledge(mock_ai_dbs):
    ai, dbs = mock_ai_dbs
    # Setup the necessary return values and side effects
    # ...
    # Call the function and assert the expected outcomes
    # ...

# Test get_improve_prompt function
def test_get_improve_prompt(mock_ai_dbs):
    ai, dbs = mock_ai_dbs
    # Setup the necessary return values and side effects
    # ...
    # Call the function and assert the expected outcomes
    # ...

  # Fixture to mock AI and DBs instances
@pytest.fixture
def mock_ai_dbs():
    ai = MagicMock(spec=AI)
    dbs = MagicMock(spec=DBs)
    return ai, dbs

# Test case when the prompt has no questions
def test_solve_prompt_no_questions(mock_ai_dbs):
    """
    Test solve_prompt_questions with a prompt that contains no questions.
    The function should return the prompt unchanged.
    """
    ai, dbs = mock_ai_dbs
    prompt = "This is a prompt with no questions."
    assert solve_prompt_questions(ai, dbs, prompt) == prompt

# Test case when the prompt has questions and the user provides valid answers
def test_solve_prompt_with_questions_and_valid_answers(mock_ai_dbs):
    """
    Test solve_prompt_questions with a prompt that contains questions and the user
    provides valid answers. The function should return the prompt with the user's
    answers replacing the questions.
    """
    ai, dbs = mock_ai_dbs
    prompt = "This is a prompt with questions:\nMORE INFO IS NEEDED:\n- Question 1\n- Question 2"
    user_answers = ["Answer 1", "Answer 2"]
    with patch('builtins.input', side_effect=user_answers):
        result = solve_prompt_questions(ai, dbs, prompt)
    assert "- Question 1\nAnswer 1" in result
    assert "- Question 2\nAnswer 2" in result

# Test case when the prompt has questions and the user requests AI to answer
def test_solve_prompt_with_questions_and_ai_answers(mock_ai_dbs):
    """
    Test solve_prompt_questions with a prompt that contains questions and the user
    requests AI to answer by writing '@AI'. The function should return the prompt
    with the AI's answers replacing the questions.
    """
    ai, dbs = mock_ai_dbs
    prompt = "This is a prompt with questions:\nMORE INFO IS NEEDED:\n- Question 1\n- Question 2"
    ai_answers = ["AI Answer 1", "AI Answer 2"]
    ai_chat_responses = [MagicMock(content=ai_answers[0]), MagicMock(content=ai_answers[1])]
    ai_chat_side_effects = [ai_chat_responses[0], ai_chat_responses[1]]
    with patch('gpt_engineer.core.step.chat.ai_chat', side_effect=ai_chat_side_effects):
        with patch('builtins.input', side_effect=["@AI", "@AI"]):
            result = solve_prompt_questions(ai, dbs, prompt)
    assert "- Question 1\nAI Answer 1" in result
    assert "- Question 2\nAI Answer 2" in result

# Test case when the prompt has questions and the user leaves them blank to be removed
def test_solve_prompt_with_questions_and_blank_answers(mock_ai_dbs):
    """
    Test solve_prompt_questions with a prompt that contains questions and the user
    leaves them blank to be removed. The function should return the prompt with the
    questions removed.
    """
    ai, dbs = mock_ai_dbs
    prompt = "This is a prompt with questions:\nMORE INFO IS NEEDED:\n- Question 1\n- Question 2"
    with patch('builtins.input', side_effect=["", ""]):
        result = solve_prompt_questions(ai, dbs, prompt)
    assert "- Question 1" not in result
    assert "- Question 2" not in result

# Test case when the prompt has questions and the user provides invalid input
def test_solve_prompt_with_questions_and_invalid_input(mock_ai_dbs):
    """
    Test solve_prompt_questions with a prompt that contains questions and the user
    provides invalid input. The function should handle the invalid input and proceed
    with the next question or end the process.
    """
    ai, dbs = mock_ai_dbs
    prompt = "This is a prompt with questions:\nMORE INFO IS NEEDED:\n- Question 1\n- Question 2"
    user_input = ["Invalid input", ""]
    with patch('builtins.input', side_effect=user_input):
        result = solve_prompt_questions(ai, dbs, prompt)
    assert "- Question 1" not in result
    assert "- Question 2" not in result

# Test case when the AI or DBs instances raise exceptions
def test_solve_prompt_with_exceptions(mock_ai_dbs):
    """
    Test solve_prompt_questions with a prompt that contains questions and the AI
    or DBs instances raise exceptions. The function should handle the exceptions
    and return an appropriate error message or raise an exception.
    """
    ai, dbs = mock_ai_dbs
    prompt = "This is a prompt with questions:\nMORE INFO IS NEEDED:\n- Question 1\n- Question 2"
    ai.side_effect = Exception("AI error")
    with patch('builtins.input', return_value="@AI"):
        with pytest.raises(Exception) as excinfo:
            solve_prompt_questions(ai, dbs, prompt)
    assert "AI error" in str(excinfo.value)