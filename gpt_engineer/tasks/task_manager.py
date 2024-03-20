from gpt_engineer.core.settings import GPTEngineerSettings
from gpt_engineer.api.model import Chat
from typing import List

class TaskManager:

    def __init__(self, settings: GPTEngineerSettings):
        self.settings = settings
        self.task_path = f"{settings.gpteng_path}/tasks"

    def create_task(self, task_id, chat: Chat):
        task_file = os.path.join(self.tasks_dir, f'task-{task_id}.md')
        with open(task_file, 'w') as f:
            f.write(chat.to_markdown())
        return task_file

    def read_task(self, task_id):
        pass

    def update_task(self, task_id, chats: List[Chat]):
        pass

    def delete_task(self, task_id):
        pass