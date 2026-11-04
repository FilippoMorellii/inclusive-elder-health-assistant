import logging
from app.config import LOG_LEVEL


def setup_logger() -> logging.Logger:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=LOG_LEVEL,
    )
    # Telegram library is very chatty at INFO level — quiet it down
    logging.getLogger("httpx").setLevel(logging.WARNING)
    return logging.getLogger("elder_bot")


logger = setup_logger()