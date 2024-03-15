import logging
import pytest
import os
from unittest.mock import patch, MagicMock

from gpt_engineer.core.db import DB
from gpt_engineer.core.dbs import DBs

from gpt_engineer.knowledge.knowledge_loader import KnowledgeLoader

# Fixture to mock AI and DBs instances

path = "tests/knowledge"
def list_path_files():
    file_paths = []
    for root, dirs, files in os.walk(path):
        for file in files:
            full_file_path = os.path.join(root, file)
            file_paths.append(full_file_path)
    return file_paths
    
@pytest.fixture
def mock_ai_dbs():
    dbs = MagicMock(spec=DBs)
    dbs.preprompts = DB("gpt_engineer/preprompts")
    return dbs

def unique(_key, docs):
    lst = [doc.metadata.get(_key) for doc in docs]
    return list(dict.fromkeys(lst))

def test_knowledge_loader(mock_ai_dbs):
    loader = KnowledgeLoader(path)
    all_paths = [file_path for file_path in list_path_files() if ".venv" not in file_path]
    
    docs = loader.load()
    languages = unique('language', docs)
    loaders = unique('loader_type', docs)
    sources = unique('source', docs)

    assert "python" in languages
    assert "markdown" in languages
    assert "js" in languages
    assert "java" in languages
    assert "markdown" in languages
    assert "txt" in languages

    assert "code" in loaders
    assert "text" in loaders

    assert sorted(all_paths) == sorted(sources)

    for ix, doc in enumerate(docs):
        if doc.metadata.get("ix"):
            raise ValueError(f"Duplocated document {doc.metadata}")
        doc.metadata["ix"] = ix

def test_list_reposiroty_files():
    all_paths = [file_path for file_path in list_path_files() if ".venv" not in file_path]

    loader = KnowledgeLoader(path)
    all_files = loader.list_repository_files()
    
    
    assert sorted(all_files) == sorted(all_paths)
    