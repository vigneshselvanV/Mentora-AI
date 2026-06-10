import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "paste-your-key-here")

FREE_MODELS = [
    "openrouter/owl-alpha"
]
