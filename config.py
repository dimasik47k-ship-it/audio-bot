import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Для Render
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_API_URL = os.getenv("BOT_API_URL", None)
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))

BASE_DIR = Path(__file__).parent
TEMP_DIR = BASE_DIR / "temp"
FFMPEG_PATH = BASE_DIR / "ffmpeg" / "ffmpeg.exe"

TEMP_DIR.mkdir(exist_ok=True)