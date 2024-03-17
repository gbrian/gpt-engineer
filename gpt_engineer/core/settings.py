import os

class GPTEngineerSettings:
    project_path: str
    model: str
    temperature: float
    steps_config: str
    role: str
    improve_mode: bool
    lite_mode: bool
    azure_endpoint: str
    chat_mode: bool
    use_git: bool
    prompt_file: str
    verbose: bool
    prompt: bool
    file_selector: bool
    api: bool
    port: int
    test: str
    build_knowledge: bool
    update_summary: bool
    find_files: bool

    def __init__(self, **kwrgs):
        if kwrgs:
            keys = GPTEngineerSettings().__dict__.keys()
            for key in kwrgs.keys():
              self.__dict__[key] = kwrgs.get(key)

    @classmethod
    def from_env(cls):
      keys = GPTEngineerSettings().__dict__.keys()
      gpt_envs = [env for env in os.environ if env.startswith("GPTARG_")]
      envs = [(env.replace("GPTARG_", ""), os.environ[env]) for env in gpt_envs]
      return GPTEngineerSettings(**dict(envs))

    def to_env(self) -> [str]:
      keys = self.__dict__.keys()
      gpt_envs = [f"GPTARG_{key}=\"{self.__dict__[key]}\"" for key in keys]
      return gpt_envs
