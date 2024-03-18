from pydantic import BaseModel
from gpt_engineer.core.settings import GPTEngineerSettings

class Settings(BaseModel, GPTEngineerSettings):
  pass