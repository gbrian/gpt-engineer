import textwrap

from gpt_engineer.core.chat_to_files import to_files_and_memory, get_code_strings, Edit
from gpt_engineer.cli.file_selector import FILE_LIST_NAME

from unittest.mock import MagicMock


class DummyDBs:
    memory = {}
    logs = {}
    preprompts = {}
    input = {}
    workspace = {}
    archive = {}
    project_metadata = {}


def test_to_files_and_memory():
    chat = textwrap.dedent(
        """
    This is a sample program.

    file1.py
    ```python
    print("Hello, World!")
    ```

    file2.py
    ```python
    def add(a, b):
        return a + b
    ```
    """
    )

    dbs = DummyDBs()
    to_files_and_memory(chat, dbs)

    assert dbs.memory["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "file2.py": "def add(a, b):\n    return a + b\n",
        "README.md": "\nThis is a sample program.\n\nfile1.py\n",
    }

    for file_name, file_content in expected_files.items():
        assert dbs.workspace[file_name] == file_content


def test_to_files_with_square_brackets():
    chat = textwrap.dedent(
        """
    This is a sample program.

    [file1.py]
    ```python
    print("Hello, World!")
    ```

    [file2.py]
    ```python
    def add(a, b):
        return a + b
    ```
    """
    )
    dbs = DummyDBs()
    to_files_and_memory(chat, dbs)

    assert dbs.memory["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "file2.py": "def add(a, b):\n    return a + b\n",
        "README.md": "\nThis is a sample program.\n\n[file1.py]\n",
    }

    for file_name, file_content in expected_files.items():
        assert dbs.workspace[file_name] == file_content


def test_files_with_brackets_in_name():
    chat = textwrap.dedent(
        """
    This is a sample program.

    [id].jsx
    ```javascript
    console.log("Hello, World!")
    ```
    """
    )

    dbs = DummyDBs()
    to_files_and_memory(chat, dbs)

    assert dbs.memory["all_output.txt"] == chat

    expected_files = {
        "[id].jsx": 'console.log("Hello, World!")\n',
        "README.md": "\nThis is a sample program.\n\n[id].jsx\n",
    }

    for file_name, file_content in expected_files.items():
        assert dbs.workspace[file_name] == file_content


def test_files_with_file_colon():
    chat = textwrap.dedent(
        """
    This is a sample program.

    [FILE: file1.py]
    ```python
    print("Hello, World!")
    ```
    """
    )

    dbs = DummyDBs()
    to_files_and_memory(chat, dbs)

    assert dbs.memory["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "README.md": "\nThis is a sample program.\n\n[FILE: file1.py]\n",
    }

    for file_name, file_content in expected_files.items():
        assert dbs.workspace[file_name] == file_content


def test_files_with_back_tick():
    chat = textwrap.dedent(
        """
    This is a sample program.

    `file1.py`
    ```python
    print("Hello, World!")
    ```
    """
    )

    dbs = DummyDBs()
    to_files_and_memory(chat, dbs)

    assert dbs.memory["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "README.md": "\nThis is a sample program.\n\n`file1.py`\n",
    }

    for file_name, file_content in expected_files.items():
        assert dbs.workspace[file_name] == file_content


def test_files_with_newline_between():
    chat = textwrap.dedent(
        """
    This is a sample program.

    file1.py

    ```python
    print("Hello, World!")
    ```
    """
    )

    dbs = DummyDBs()
    to_files_and_memory(chat, dbs)

    assert dbs.memory["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "README.md": "\nThis is a sample program.\n\nfile1.py\n\n",
    }

    for file_name, file_content in expected_files.items():
        assert dbs.workspace[file_name] == file_content


def test_files_with_newline_between_header():
    chat = textwrap.dedent(
        """
    This is a sample program.

    ## file1.py

    ```python
    print("Hello, World!")
    ```
    """
    )

    dbs = DummyDBs()
    to_files_and_memory(chat, dbs)

    assert dbs.memory["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "README.md": "\nThis is a sample program.\n\n## file1.py\n\n",
    }

    for file_name, file_content in expected_files.items():
        assert dbs.workspace[file_name] == file_content


def test_get_code_strings(monkeypatch):
    # arrange
    mock_db = MagicMock()
    mock_db.path = "path/to"
    data = {"file1.txt": "This is file 1 content", "file2.txt": "This is file 2 content"}
    mock_db.__getitem__ = lambda self, x: data.get(x)
    mock_db.__contains__ = lambda self, x: x in data

    mock_metadata_db = {FILE_LIST_NAME: "path/to/file1.txt\npath/to/file2.txt"}

    def mock_get_all_files_in_dir(directory):
        return ["path/to/file1.txt", "path/to/file2.txt"]

    def mock_open_file(path):
        return f"File Data for file: {path}"

    monkeypatch.setattr(
        "gpt_engineer.core.chat_to_files._get_all_files_in_dir", mock_get_all_files_in_dir
    )

    monkeypatch.setattr("gpt_engineer.core.chat_to_files._open_file", mock_open_file)

    # act
    result = get_code_strings(mock_db, mock_metadata_db)

    print(result)
    # assert
    assert result["file1.txt"] == "File Data for file: path/to/file1.txt"
    assert result["file2.txt"] == "File Data for file: path/to/file2.txt"


def test_parse_all_edits_single_diff():
    input_text = "This is an example response with a diff syntax inside\n\nOUTPUT:\n```python\ncli/file_selector.py\n<<<<<<< HEAD\n    ## Section to change\n=======\n    ## Secrion with a change\n>>>>>>> updated\n```"
    expected_output = [
        Edit(
            filename="cli/file_selector.py",
            before="## Section to change",
            after="## Secrion with a change",
            full_text="cli/file_selector.py\n<<<<<<< HEAD\n    ## Section to change\n=======\n    ## Secrion with a change\n>>>>>>> updated",
        )
    ]
    assert parse_all_edits(input_text) == expected_output


def test_parse_all_edits_multiple_diffs():
    input_text = "This is an example response with a diff syntax inside\n\nOUTPUT:\n```python\ncli/file_selector.py\n<<<<<<< HEAD\n    ## Section to change\n=======\n    ## Secrion with a change\n>>>>>>> updated\n```\n\nMore comments\n\n```python\n<<<<<<< HEAD\n    ## Section to change\n=======\n    ## Secrion with a change\n>>>>>>> updated\n```"
    expected_output = [
        Edit(
            filename="cli/file_selector.py",
            before="## Section to change",
            after="## Secrion with a change",
            full_text="cli/file_selector.py\n<<<<<<< HEAD\n    ## Section to change\n=======\n    ## Secrion with a change\n>>>>>>> updated",
        ),
        Edit(
            filename="",
            before="## Section to change",
            after="## Secrion with a change",
            full_text="<<<<<<< HEAD\n    ## Section to change\n=======\n    ## Secrion with a change\n>>>>>>> updated",
        ),
    ]
    assert parse_all_edits(input_text) == expected_output


def test_parse_all_edits_diffs_with_code():
    input_text = 'This is an example response with a diff syntax inside\n\nOUTPUT:\n```python\ncli/file_selector.py\n<<<<<<< HEAD\n    ```python\n    cli/file_selector.py\n        def this_is_python_code:\n            pass\n    ```\n=======\n    ```python\n    cli/file_selector.py\n        def this_is_python_code:\n            """ A python function """\n            pass\n    ```\n>>>>>>> updated\n```\n\nMore comments\n\n```python\n<<<<<<< HEAD\n    ## Section to change\n=======\n    ## Secrion with a change\n>>>>>>> updated\n```'
    expected_output = [
        Edit(
            filename="cli/file_selector.py",
            before="```python\n    cli/file_selector.py\n        def this_is_python_code:\n            pass\n    ```",
            after='```python\n    cli/file_selector.py\n        def this_is_python_code:\n            """ A python function """\n            pass\n    ```',
            full_text='cli/file_selector.py\n<<<<<<< HEAD\n    ```python\n    cli/file_selector.py\n        def this_is_python_code:\n            pass\n    ```\n=======\n    ```python\n    cli/file_selector.py\n        def this_is_python_code:\n            """ A python function """\n            pass\n    ```\n>>>>>>> updated',
        ),
        Edit(
            filename="",
            before="## Section to change",
            after="## Secrion with a change",
            full_text="<<<<<<< HEAD\n    ## Section to change\n=======\n    ## Secrion with a change\n>>>>>>> updated",
        ),
    ]
    assert parse_all_edits(input_text) == expected_output
