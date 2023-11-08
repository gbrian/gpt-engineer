import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL") or "gpt-4"
TEMPERATURE = float(os.getenv("TEMPERATURE") or 0.1)
