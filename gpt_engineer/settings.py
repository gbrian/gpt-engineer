import os
import logging
import openai

from dotenv import load_dotenv

#Disable chroma telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Load .env file
load_dotenv()

# SETTINGS
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL") or "gpt-4"
TEMPERATURE = float(os.getenv("TEMPERATURE") or 0.1)

GPT_ENGINEER_METADATA_PATH=os.getenv("GPT_ENGINEER_METADATA_PATH")
KNOWLEDGE_PATH = f"{GPT_ENGINEER_METADATA_PATH}/knowledge"

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
logger.info(f'GPT Engineer Metadata Path: {GPT_ENGINEER_METADATA_PATH}')
logger.info(f'Knowledge Path: {KNOWLEDGE_PATH}')
