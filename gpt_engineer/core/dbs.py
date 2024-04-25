import datetime
import shutil

from dataclasses import dataclass

from gpt_engineer.core.db import DB, DBPrompt
from gpt_engineer.core.settings import GPTEngineerSettings

# dataclass for all dbs:
@dataclass
class DBs:
    memory: DB
    logs: DB
    preprompts: DB
    roles: DB
    input: DBPrompt
    workspace: DB
    archive: DB
    project_metadata: DB
    settings: GPTEngineerSettings

def archive(dbs: DBs) -> None:
    """
    Archive the memory and workspace databases.

    Parameters
    ----------
    dbs : DBs
        The databases to archive.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.move(
        str(dbs.memory.path), str(dbs.archive.path / timestamp / dbs.memory.path.name)
    )

    exclude_dir = ".gpteng"
    items_to_copy = [f for f in dbs.workspace.path.iterdir() if not f.name == exclude_dir]

    for item_path in items_to_copy:
        destination_path = dbs.archive.path / timestamp / item_path.name
        if item_path.is_file():
            shutil.copy2(item_path, destination_path)
        elif item_path.is_dir():
            shutil.copytree(item_path, destination_path)

    return []
