import pytest

from gpt_engineer.knowledge.knowledge_code_splitter import KnowledgeCodeSplitter

def test_java ():
    code_splitter = KnowledgeCodeSplitter()
    docs = code_splitter.load('tests/knowledge/dummy_code_java_2.java')
    assert docs[0].metadata['language'] == 'java'

def test_js ():
    code_splitter = KnowledgeCodeSplitter()
    docs = code_splitter.load('tests/knowledge/dummy_code.js')
    assert docs[0].metadata['language'] == 'js'

def test_ts ():
    code_splitter = KnowledgeCodeSplitter()
    docs = code_splitter.load('tests/knowledge/dummy_code.ts')
    assert docs[0].metadata['language'] == 'ts' or docs[0].metadata['language'] == 'js'

def test_python ():
    code_splitter = KnowledgeCodeSplitter()
    docs = code_splitter.load('tests/knowledge/dummy_code.py')
    assert docs[0].metadata['language'] == 'python'

def test_json ():
    code_splitter = KnowledgeCodeSplitter()
    docs = code_splitter.load('tests/knowledge/dummy_code.json')
    assert docs[0].metadata['language'] == 'js'

def test_markdown ():
    code_splitter = KnowledgeCodeSplitter()
    docs = code_splitter.load('tests/knowledge/dummy_code.md')
    assert docs[0].metadata['language'] == 'markdown'

def test_text ():
    code_splitter = KnowledgeCodeSplitter()
    fails_with_value_error = False
    docs = code_splitter.load('tests/knowledge/dummy_code.txt')
    assert docs[0].metadata['language'] == 'txt'

def test_no_extension ():
    code_splitter = KnowledgeCodeSplitter()
    fails_with_value_error = False
    docs = code_splitter.load('tests/knowledge/dummy_code')
    assert docs[0].metadata['language'] == 'txt'