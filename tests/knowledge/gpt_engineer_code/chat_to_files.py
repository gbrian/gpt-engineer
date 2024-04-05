import os
import re
import logging

from termcolor import colored

from dataclasses import dataclass
from typing import List, Tuple

from gpt_engineer.core.db import DB, DBs
from gpt_engineer.cli.file_selector import FILE_LIST_NAME


logger = logging.getLogger(__name__)


def parse_chat(chat) -> List[Tuple[str, str]]:
    """
    Extracts all code blocks from a chat and returns them
    as a list of (filename, codeblock) tuples.

    Parameters
    ----------
    chat : str
        The chat to extract code blocks from.

    Returns
    -------
    List[Tuple[str, str]]
        A list of tuples, where each tuple contains a filename and a code block.
    """
    # Get all ``` blocks and preceding filenames
    regex = r"(\S+)\n\s*```[^\n]*\n(.+?)```"
    matches = re.finditer(regex, chat, re.DOTALL)

    files = []
    for match in matches:
        # Strip the filename of any non-allowed characters and convert / to \
        path = re.sub(r'[\:<>"|?*]', "", match.group(1))

        # Remove leading and trailing brackets
        path = re.sub(r"^\[(.*)\]$", r"\1", path)

        # Remove leading and trailing backticks
        path = re.sub(r"^`(.*)`$", r"\1", path)

        # Remove trailing ]
        path = re.sub(r"[\]\:]$", "", path)

        # Get the code
        code = match.group(2)

        # Add the file to the list
        files.append((path, code))

    # Get all the text before the first ``` block
    readme = chat.split("```")[0]
    files.append(("README.md", readme))

    # Return the files
    return files


def to_files_and_memory(chat: str, dbs: DBs):
    """
    Save chat to memory, and parse chat to extracted file and save them to the workspace.

    Parameters
    ----------
    chat : str
        The chat to parse.
    dbs : DBs
        The databases that include the memory and workspace database
    """
    dbs.memory["all_output.txt"] = chat
    to_files(chat, dbs.workspace)


def to_files(chat: str, workspace: DB):

    files = parse_chat(chat)
    for file_name, file_content in files:
        workspace[file_name] = file_content


def get_code_strings(workspace: DB, metadata_db: DB) -> dict[str, str]:

    files_paths = metadata_db[FILE_LIST_NAME].strip().split("\n")
    files = []

    for full_file_path in files_paths:
        if os.path.isdir(full_file_path):
            for file_path in _get_all_files_in_dir(full_file_path):
                files.append(file_path)
        else:
            files.append(full_file_path)

    files_dict = {}

    for path in files:
        assert os.path.commonpath([full_file_path, workspace.path]) == str(
            workspace.path
        ), "Trying to edit files outside of the workspace"

        file_name = os.path.relpath(path, workspace.path)

        if file_name in workspace:
            try:
                files_dict[file_name] = _open_file(path)
            except:
                logger.error(f"Invalid file or can't read {path}")

    return files_dict


def format_file_to_input(file_name: str, file_content: str) -> str:
    
    file_str = f"""
    {file_name}
    ```
    {file_content}
    ```
    """
    return file_str


def overwrite_files_with_edits(chat: str, dbs: DBs):
    edits = parse_edits(chat)
    apply_edits(edits, dbs.workspace)


@dataclass
class Edit:
    filename: str
    before: str
    after: str
    full_text: str


def parse_edits(llm_response):
    def parse_one_edit(lines, parse_type="file"):
        full_text = "\n".join(lines)
        HEAD = "<<<<<<< HEAD"
        DIVIDER = "======="
        UPDATE = ">>>>>>> updated"

        logger.info(f"parse_one_edit {parse_type}: {lines}")
        is_file_change = True if HEAD in lines else False
        if is_file_change:
            filename = lines.pop(0)
            text = "\n".join(lines)
            splits = text.split(DIVIDER)
            if len(splits) != 2:
                raise ValueError(f"Could not parse following text as code edit: \n{text}")
            before, after = splits

            before = before.replace(HEAD, "").strip()
            after = after.replace(UPDATE, "").strip()

            return Edit(filename, before, after, full_text)

        logger.info(f"Request user confirmation to execute {lines}")
        return None

    def parse_all_edits(txt):
        edits = []
        current_edit = []
        in_fence = None
        is_patch = False

        for line in txt.split("\n"):
            if line.startswith("<<<<<<<"):
                is_patch = True
            if line.startswith(">>>>>>>"):
                is_patch = False
            if line.startswith("```") and in_fence and not is_patch:
                edits.append(parse_one_edit(current_edit, parse_type=in_fence))
                current_edit = []
                in_fence = False
                continue
            elif line.startswith("```") and not in_fence:
                in_fence = line[3:]
                continue

            if in_fence:
                current_edit.append(line)

        return [edit for edit in edits if edit]

    return parse_all_edits(llm_response)


def apply_edits(edits: List[Edit], workspace: DB):
    for edit in edits:
        success, error_message = apply_edit(edit=edit, workspace=workspace)
        if not success:
            input(error_message)

def apply_edit(edit: Edit, workspace: DB)
    filename = edit.filename
    logger.info(f"apply_edits NEW FILE {edit}")
    if edit.before == "":
        if workspace.get(filename) is not None:
            return False, f"The edit to be applied wants to create a new file `{filename}`, but that already exists."
        workspace[filename] = edit.after  # new file
    else:
        if workspace[filename].count(edit.before) > 1:
            logger.warn(
                f"While applying an edit to `{filename}`, the code block to be replaced was found multiple times. All instances will be replaced."
            )
        curr_file = workspace[filename]
        workspace[filename] = curr_file.replace(
            edit.before, edit.after
        )  # existing file
        if curr_file == workspace[filename]:
            error = f"""
            {colored(f"change not applied to file {filename}", "red")}
            {edit.full_text}
            {colored(f"Apply manually and press Enter to continue", "green")}
            """
            return True, error
    return True, None

def _get_all_files_in_dir(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)
    for dir in dirs:
        yield from _get_all_files_in_dir(os.path.join(root, dir))


def _open_file(file_path) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        raise ValueError(
            f"Non-text file detected: {file_path}, gpt-engineer currently only supports utf-8 decodable text files."
        )
