import sys
import re
import logging

from gpt_engineer.core.settings import GPTEngineerSettings
from gpt_engineer.api.app import GPTEngineerAPI

gptEngineerArgs = GPTEngineerSettings.from_env()
logging.info(f"API main, settings {gptEngineerArgs.__dict__}")

app = GPTEngineerAPI(gptEngineerArgs).start()