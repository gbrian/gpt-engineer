import os
import logging
import importlib.util

from dotenv import load_dotenv

#Disable chroma telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Load .env file
load_dotenv()

PROMPT_FILE=os.getenv("PROMPT_FILE") or "prompt"
PROJECT_SUMMARY=os.getenv("PROJECT_SUMMARY") or "project_summary.md"
HISTORY_PROMPT_FILE = os.getenv("HISTORY_PROMPT_FILE")
if not HISTORY_PROMPT_FILE:
  HISTORY_PROMPT_FILE = f"history.{PROMPT_FILE}"

# SETTINGS
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
MODEL = os.getenv("MODEL") or "gpt-4"
KNOWLEDGE_MODEL = os.getenv("KNOWLEDGE_MODEL") or "gpt-3.5-turbo"
TEMPERATURE = float(os.getenv("TEMPERATURE") or 0.1)
KNOWLEDGE_ENRICH_DOCUMENTS = True if os.getenv("KNOWLEDGE_ENRICH_DOCUMENTS", None) is not None else False
KNOWLEDGE_EXTRACT_DOCUMENTS_TAGS = True if os.getenv("KNOWLEDGE_EXTRACT_DOCUMENTS_TAGS", None) is not None else False
KNOWLEDGE_SEARCH_DOCUMENT_COUNT = os.getenv("KNOWLEDGE_SEARCH_DOCUMENT_COUNT", 10)
KNOWLEDGE_SEARCH_TYPE = os.getenv("KNOWLEDGE_SEARCH_TYPE", "similarity")  # Also test "mmr"

GPT_ENGINEER_METADATA_PATH=os.getenv("GPT_ENGINEER_METADATA_PATH")
GPTENG_PATH=f"{GPT_ENGINEER_METADATA_PATH}/.gpteng" if GPT_ENGINEER_METADATA_PATH else ".gpteng"

VALID_FILE_EXTENSIONS = {}
IGNORE_FOLDERS = {}

LANGUAGE_FROM_EXTENSION = {
    "py": "python",
    "java": "java",
    "js": "js",
    "cpp": "cpp",
    "go": "go",
    "rb": "ruby",
    "php": "php",
    "swift": "swift",
    "kt": "kotlin",
    "rs": "rust",
    "sh": "shell",
    "r": "r",
    "pl": "perl",
    "scala": "scala",
    "ts": "ts",
    "md": "markdown",
    "txt": "text",
    "html": "html"
}

KNOWLEDGE_FILE_IGNORE = { 
    "site-packages/",
    "node_modules/",
    "venv/",
    ".vscode/",
    ".gpteng/",
    ".git/",
    ".env"
}

KNOWLEDGE_CONTEXT_CUTOFF_RELEVANCE_SCORE=0.7

# Add a new setting for CHAT_FILE
CHAT_FILE = os.getenv('CHAT_FILE', 'chat')

# Provider to read project files
# Options: 
#   git: Will use "git ls-files"
#   os: Will use Python to traverse (not implemented) 
FILE_PROVIDER="git"

# File to store selected files for the task
FILE_LIST_NAME = "file_list.txt"

USE_AI_CACHE=True if os.getenv("USE_AI_CACHE", "False") == "True" else False

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

level = logging.DEBUG if os.getenv("DEBUG") in ["1", "true", "True"] else None
logging.basicConfig(level=level)

# LOGGING
logger = logging.getLogger(__name__)
logger.info(f'Logging level: {level}: {os.getenv("DEBUG")}')
logger.info(f'Working directory: {os.getcwd()}')
logger.info(f'OpenAI API Key: {OPENAI_API_KEY}')
logger.info(f'Model: {MODEL}')
logger.info(f'KNOWLEDGE_MODEL: {KNOWLEDGE_MODEL}')
logger.info(f'Temperature: {TEMPERATURE}')
logger.info(f'GPT Engineer Metadata Path: {GPTENG_PATH}')
logger.info(f'Knowledge Path: {GPTENG_PATH}/knowled_path_list')
logger.info(f'Knowledge enrich documents: {KNOWLEDGE_ENRICH_DOCUMENTS}')
logger.info(f'Knowledge enrich documents with tags: {KNOWLEDGE_EXTRACT_DOCUMENTS_TAGS}')
logger.info(f'Knowledge search document count: {KNOWLEDGE_SEARCH_DOCUMENT_COUNT}')
logger.info(f'Knowledge search type: {KNOWLEDGE_SEARCH_TYPE}')


logger.info(f'Prompt file: {PROMPT_FILE}')
logger.info(f'History prompt file: {PROMPT_FILE}')
logger.info(f'Knowledge Path: {HISTORY_PROMPT_FILE}')


logger.info(f"Settings overrided: {settings_overrided}")
