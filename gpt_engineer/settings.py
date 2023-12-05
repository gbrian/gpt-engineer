import os
import openai

from dotenv import load_dotenv

# Load .env file
load_dotenv()

# SETTINGS
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL") or "gpt-4"
TEMPERATURE = float(os.getenv("TEMPERATURE") or 0.1)

GPT_ENGINEER_METADATA_PATH=os.getenv("GPT_ENGINEER_METADATA_PATH")

## INITIALIZE
openai.api_key = OPENAI_API_KEY
