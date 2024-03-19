from gpt_engineer.core.settings import GPTEngineerSettings

class TaskManager:

    def __init__(self, settings: GPTEngineerSettings):
        self.settings = settings
        self.task_path = f"{settings.project_path}/.gpteng/tasks"

    def create_task(self, task_id, chat: Chat):
        task_file = os.path.join(self.tasks_dir, f'task-{task_id}.md')
        with open(task_file, 'w') as f:
            f.write(chat.to_markdown())
        return task_file

    def read_task(self, task_id):
        # TODO: Implement method to read a task

    def update_task(self, task_id, chats: List[Chat]):
        # TODO: Implement method to update a task

    def delete_task(self, task_id):
        # TODO: Implement method to delete a task