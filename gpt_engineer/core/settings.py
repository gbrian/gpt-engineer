import os
import json
import logging
import pathlib
from gpt_engineer import settings

class GPTEngineerSettings:
    project_name: str
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
    gpteng_path: str
    openai_api_key: str
    openai_api_base: str
    knowledge_extract_document_tags: bool
    knowledge_search_type: str
    knowledge_search_document_count: int
    knowledge_context_cutoff_relevance_score: float
    knowledge_external_folders: str
    watching: bool
    use_knowledge: bool
    log_ai: bool

    def __init__(self, **kwrgs):
        self.project_name = None
        self.project_path = "."
        self.openai_api_key = settings.OPENAI_API_KEY
        self.openai_api_base = settings.OPENAI_API_BASE
        self.knowledge_extract_document_tags = False
        self.knowledge_search_type = settings.KNOWLEDGE_SEARCH_TYPE
        self.knowledge_search_document_count = settings.KNOWLEDGE_SEARCH_DOCUMENT_COUNT
        self.temperature = settings.TEMPERATURE
        self.model = settings.MODEL
        self.knowledge_file_ignore = ",".join(settings.KNOWLEDGE_FILE_IGNORE)
        self.gpteng_path = "./.gpteng"
        self.knowledge_enrich_documents = settings.KNOWLEDGE_ENRICH_DOCUMENTS
        self.knowledge_context_cutoff_relevance_score = settings.KNOWLEDGE_CONTEXT_CUTOFF_RELEVANCE_SCORE
        self.knowledge_external_folders = ""
        self.watching = False
        self.use_knowledge = True
        self.log_ai = False
        if kwrgs:
            keys = GPTEngineerSettings().__dict__.keys()
            for key in kwrgs.keys():
              self.__dict__[key] = kwrgs.get(key)

    @classmethod
    def from_env(cls):
      base = GPTEngineerSettings()
      gpt_envs = [env for env in os.environ if env.startswith("GPTARG_")]
      envs = [(env.replace("GPTARG_", ""), os.environ[env]) for env in gpt_envs]
      for k, v in envs:
        base.__dict__[k] = v
      return base

    @classmethod
    def from_project(cls, gpteng_path: str):
        base = GPTEngineerSettings()
        base.gpteng_path = gpteng_path
        base.project_path = gpteng_path
        with open(f"{gpteng_path}/project.json", 'r') as f:
          settings = json.loads(f.read())
          gpt_settings = GPTEngineerSettings(**{ **base.__dict__, **settings })
          if not gpt_settings.project_name:
              gpt_settings.project_name = gpt_settings.project_path.split("/")[-1]
          return gpt_settings
    
    @classmethod
    def from_json(cls, settings: dict):
      base = GPTEngineerSettings.from_env()
      return GPTEngineerSettings(**{ **base.__dict__, **settings })

    def to_env(self) -> [str]:
      keys = self.__dict__.keys()
      gpt_envs = [f"GPTARG_{key}=\"{self.__dict__[key]}\"" for key in keys]
      return gpt_envs

    def save_project(self):
      settings = self.__dict__
      path = f"{self.gpteng_path}/project.json"
      logging.info(f"Saving project {path} {settings}")
      with open(path, 'w') as f:
        f.write(json.dumps(settings, indent=2))

    def detect_sub_projects(self):
      try:
        return [str(project_path).replace("/.gpteng/project.json", "") for project_path in \
          pathlib.Path(self.project_path).rglob("./*/.gpteng/project.json")]
      except Exception as ex:
        log.debug(f"Error {ex}")

      return []

    def get_dbs(self):
      from gpt_engineer.core import build_dbs
      return build_dbs(settings=self)

    def get_sub_projects(self):
        try:
          self.sub_projects.split(",")
        except:
          pass
        return []