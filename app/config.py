import os
from pathlib import Path
from dotenv import load_dotenv

# Individua la cartella principale del progetto (Designed4U-bot)
# Poiché config.py è in app/, risaliamo di un livello
base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / ".env"

# Carica esplicitamente il file .env usando il percorso assoluto
load_dotenv(dotenv_path=env_path)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Minuti prima di notificare il caregiver se l'utente non conferma l'assunzione
# Default: 15 minuti
CAREGIVER_TIMEOUT_MINUTES = int(os.getenv("CAREGIVER_TIMEOUT_MINUTES", "15"))

# Minuti dello snooze del reminder
REMINDER_SNOOZE_MINUTES = 1


if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError(
        f"TELEGRAM_BOT_TOKEN is missing at {env_path}. "
        "Assicurati che il file .env esista nella cartella principale."
    )