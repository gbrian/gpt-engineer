"""
Test suite for the prompt.py module.

This test suite is designed to ensure that all functions in the prompt.py module
are working as expected, including edge cases.
"""

import pytest
from unittest.mock import patch, MagicMock
from gpt_engineer.core.step.prompt import get_prompt
from gpt_engineer.core.ai import AI
from gpt_engineer.core.dbs import DBs
from gpt_engineer.core.step.clarify import solve_prompt_questions

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
    result, _ = solve_prompt_questions(ai, dbs, prompt)
    assert result == prompt

# Test case when the prompt has questions and the user provides valid answers
def test_solve_prompt_with_questions_and_valid_answers(mock_ai_dbs):
    """
    Test solve_prompt_questions with a prompt that contains questions and the user
    provides valid answers. The function should return the prompt with the user's
    answers replacing the questions.
    """
    ai, dbs = mock_ai_dbs
    prompt = "This is a prompt with questions:\nMORE INFO NEEDED:\n- Question 1\n- Question 2"
    user_answers = ["Answer 1", "Answer 2"]
    with patch('builtins.input', side_effect=user_answers):
        result, _ = solve_prompt_questions(ai, dbs, prompt)
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
    prompt = "This is a prompt with questions:\nMORE INFO NEEDED:\n- Question 1\n- Question 2"
    ai_answers = ["AI Answer 1", "AI Answer 2"]
    ai_chat_responses = [MagicMock(content=ai_answers[0]), MagicMock(content=ai_answers[1])]
    ai_chat_side_effects = [ai_chat_responses[0], ai_chat_responses[1]]
    with patch('gpt_engineer.core.step.chat.ai_chat', side_effect=ai_chat_side_effects):
        with patch('builtins.input', side_effect=["@AI", "@AI"]):
            result, _ = solve_prompt_questions(ai, dbs, prompt)
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
    prompt = "This is a prompt with questions:\nMORE INFO NEEDED:\n- Question 1\n- Question 2"
    with patch('builtins.input', side_effect=["", ""]):
        result, _ = solve_prompt_questions(ai, dbs, prompt)
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
    prompt = "This is a prompt with questions:\nMORE INFO NEEDED:\n- Question 1\n- Question 2"
    user_input = ["Invalid input", ""]
    with patch('builtins.input', side_effect=user_input):
        result, _ = solve_prompt_questions(ai, dbs, prompt)
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
    prompt = "This is a prompt with questions:\nMORE INFO NEEDED:\n- Question 1\n- Question 2"
    ai.side_effect = Exception("AI error")
    with patch('builtins.input', return_value="@AI"):
        with pytest.raises(Exception) as excinfo:
            result, _ = solve_prompt_questions(ai, dbs, prompt)
    assert "AI error" in result

def test_solve_prompt_with_exceptions_valid_with_spaces(mock_ai_dbs):
    """
    Test solve_prompt_questions with a prompt that contains questions and the user
    provides valid answers with leading and trailing spaces. The function should return
    the prompt with the user's answers, stripped of leading and trailing spaces, replacing the questions.
    """
    ai, dbs = mock_ai_dbs
    prompt = "- Check if there are any additional context configurations or initializers that need to be specified for the test to run correctly. Sometimes, specific test configurations are required to set up the test context properly.\n\n- Review the test classpath to ensure that all necessary Spring Boot and Spring MVC dependencies are included. Missing dependencies can lead to an incomplete test context.\n\n- If you have custom context configuration or initializers, make sure they are correctly applied and do not conflict with the auto-configuration provided by `@WebMvcTest`.\n\nIf after checking these points the issue persists, you may need to provide more information for further diagnosis. In that case, append the following \"MORE INFO NEEDED\" section with these questions:\n\nMORE INFO NEEDED:\n- Is the `MroController` class properly annotated with `@RestController` and does it have any other dependencies besides `MroService`?\n- Are there any additional configurations or beans that are required for the `MroController` to work that have not been included in the test context?\n- Can you provide the full stack trace of the error for a more detailed analysis?\n- Are there any other custom annotations or context initializers used in the project that might affect the test setup?\n- Have you tried running other tests within the same project, and do they encounter similar issues with context loading?"
    user_answers = ["Yes", "No", "Here is the stack trace: ...", "No", "Yes"]
    with patch('builtins.input', side_effect=user_answers):
        result, _ = solve_prompt_questions(ai, dbs, prompt)
    assert "Q: - Is the `MroController` class properly annotated with `@RestController` and does it have any other dependencies besides `MroService`?\nA: Yes" in result
    assert "Q: - Are there any additional configurations or beans that are required for the `MroController` to work that have not been included in the test context?\nA: No" in result
    assert "Q: - Can you provide the full stack trace of the error for a more detailed analysis?\nA: Here is the stack trace: ..." in result
    assert "Q: - Are there any other custom annotations or context initializers used in the project that might affect the test setup?\nA: No" in result
    assert "Q: - Have you tried running other tests within the same project, and do they encounter similar issues with context loading?\nA: Yes" in result