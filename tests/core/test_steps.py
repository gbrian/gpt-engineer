import pytest
from unittest import mock
from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DBs
from gpt_engineer.core.steps import validate_context
from gpt_engineer.core.domain import Document

class MockAI(AI):
    def start(self, system, validate_prompt, step_name):
        return self.responses

class MockDBs(DBs):
    def __init__(self, preprompts):
        self.preprompts = preprompts

class TestValidateContext:
    def setup_method(self, method):
        self.ai = MockAI()
        self.dbs = MockDBs({"roadmap": "roadmap", "philosophy": "philosophy", "validate_context": "{prompt} {context}"})
        self.prompt = "prompt"
        self.doc = Document(page_content="context")

    def teardown_method(self, method):
        pass

    def test_empty_response(self):
        self.ai.responses = [""]
        result = validate_context(self.ai, self.dbs, self.prompt, self.doc)
        assert result is None

    def test_not_relevant_response(self):
        self.ai.responses = ["NOT RELEVANT"]
        result = validate_context(self.ai, self.dbs, self.prompt, self.doc)
        assert result is None

    def test_relevant_response(self):
        self.ai.responses = ["relevant"]
        result = validate_context(self.ai, self.dbs, self.prompt, self.doc)
        assert result is self.doc
        assert self.doc.page_content == "relevant"