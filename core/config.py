"""App-wide settings. Tweak these instead of hunting through the code."""
from pathlib import Path

APP_NAME = "VibeSync"
TAGLINE = "Boredom.exe has stopped working."
TIMEZONE = "Asia/Kolkata"

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"          # runtime JSON lives here (git-ignored)

# Lounge (social room) tuning
CHAT_REFRESH_SECONDS = 3          # how often the Lounge (chat, poll, members) refreshes
ONLINE_WINDOW_SECONDS = 20        # "online" if seen within this window
MAX_MESSAGES = 200                # per room, oldest trimmed first
MAX_MESSAGE_LEN = 300
MAX_NAME_LEN = 20
ROOM_TTL_HOURS = 24               # idle rooms are cleaned up after this
SYNC_COUNTDOWN_SECONDS = 10       # "Sync start" countdown length
