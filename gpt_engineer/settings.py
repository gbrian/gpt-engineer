import os
import logging
import openai
import importlib.util

from dotenv import load_dotenv

#Disable chroma telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Load .env file
load_dotenv()

PROMPT_FILE=os.getenv("PROMPT_FILE") or "prompt"
HISTORY_PROMPT_FILE = os.getenv("HISTORY_PROMPT_FILE")
if not HISTORY_PROMPT_FILE:
  HISTORY_PROMPT_FILE = f"history.{PROMPT_FILE}"

# SETTINGS
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL") or "gpt-4"
TEMPERATURE = float(os.getenv("TEMPERATURE") or 0.1)

GPT_ENGINEER_METADATA_PATH=os.getenv("GPT_ENGINEER_METADATA_PATH") or "."
GPTENG_PATH=f"{GPT_ENGINEER_METADATA_PATH}/.gpteng"

# Valid files to work and index
VALID_FILE_EXTENSIONS = [
    ".py", ".java", ".js", ".c", ".cpp", ".cs", ".go", ".rb", ".php", ".swift", ".kt", ".rs", ".sh", ".r", ".pl", ".scala", ".ts",
    ".md", ".txt", ".html", ".css", ".xml", ".json", ".yml", ".csv", ".sql", ".bat", ".ps1", ".vbs", ".log", ".ini", ".conf", ".cfg",
    ".tex", ".rtf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf"
]

# Used by knowledge to split documents
PROJECT_LANGUAGE = "python"

IGNORE_FOLDERS = { "site-packages", "node_modules", "venv", ".vscode", ".gpteng" }
IGNORE_FILES = { }

# File to store selected files for the task
FILE_LIST_NAME = "file_list.txt"

#################################################
## User override
## Try to import settings from 
## .gteng/settings.py in the working directory
#################################################
settings_overrided = []
try:
    spec = importlib.util.spec_from_file_location("local_settings", f"{GPTENG_PATH}/settings.py")
    local_settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(local_settings)
    # Update global settings with local settings
    for key, value in local_settings.__dict__.items():
        if key.isupper():
            globals()[key] = value
            settings_overrided.append(key)
except FileNotFoundError:
    pass

## INITIALIZE
openai.api_key = OPENAI_API_KEY

level = logging.DEBUG if os.getenv("DEBUG") is not None else logging.INFO
logging.basicConfig(level=level)

# LOGGING
logger = logging.getLogger(__name__)
logger.info(f'Working directory: {os.getcwd()}')
logger.info(f'OpenAI API Key: {OPENAI_API_KEY}')
logger.info(f'Model: {MODEL}')
logger.info(f'Temperature: {TEMPERATURE}')
logger.info(f'GPT Engineer Metadata Path: {GPTENG_PATH}')
logger.info(f'Knowledge Path: {GPTENG_PATH}/knowled_path_list')

logger.info(f'Prompt file: {PROMPT_FILE}')
logger.info(f'History prompt file: {PROMPT_FILE}')
logger.info(f'Knowledge Path: {HISTORY_PROMPT_FILE}')


logger.info(f"Settings overrided: {settings_overrided}")
