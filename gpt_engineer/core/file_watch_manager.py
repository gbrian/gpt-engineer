import os
import logging
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from gpt_engineer.core.settings import GPTEngineerSettings

from gpt_engineer.knowledge.knowledge_loader import KnowledgeLoader

class FileWatchManager(FileSystemEventHandler):
    def __init__(self, project_paths: [GPTEngineerSettings], callback):
        self.project_paths = project_paths
        self.event_handler = self
        self.callback = callback
        self.observer = Observer()
        self.last_modified = datetime.now()

    def start(self):
        return
        for project_path in self.project_paths:
            self.observer_project(project_path=project_path)
        logging.info(f"file_watch_manager start watching {self.project_paths}")
        self.observer.start()

    def observer_project(self, project_path: str):
        logging.info(f"Open observe project {project_path}")
        settings = GPTEngineerSettings.from_project(gpteng_path=project_path)
        loader = KnowledgeLoader(settings=settings)
        folders = loader.list_repository_folders()
        for folder_path in folders:
            self.observer.schedule(self.event_handler, folder_path, recursive=False)


    def stop(self):
        logging.info(f"file_watch_manager STOP watching")
        self.observer.stop()
        self.observer.join()
        logging.info(f"file_watch_manager STOPPED")

    def on_modified(self, event):
        if event.is_directory:
            return
        if not isinstance(event, FileModifiedEvent):
            return
        if datetime.now() - self.last_modified < timedelta(seconds=1):
            return
        self.last_modified = datetime.now()
        logging.info(f"file_watch_manager change detected {event}")
        file_path = event.src_path
        project_path = [path for path in self.paths if file_path.startswith(path)][0]
        callback(project_path, file_path)

