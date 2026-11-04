"""Validatori riutilizzabili per gli input degli utenti."""
import re

# Pattern 1: ora + separatore + minuti (es. "8:30", "8.30", "8 30", "8 e 30")
# I minuti DEVONO essere 2 cifre per evitare ambiguità (8:3 = 8:03 o 8:30?)
TIME_PATTERN_FULL = re.compile(
    r"""
    ^\s*
    (\d{1,2})                              # ore: 1 o 2 cifre
    \s*
    (?: : | \. | - | h | \s+e\s+ | \s+ )   # separatore
    \s*
    (\d{2})                                # minuti: 2 cifre obbligatorie
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Pattern 2: solo ora (es. "8", "08") → interpretato come HH:00
TIME_PATTERN_HOUR_ONLY = re.compile(r"^\s*(\d{1,2})\s*$")


def parse_time(text: str) -> str | None:
    # Prova a interpretare un input dell'utente come orario.
    # Ritorna l'orario normalizzato come stringa "HH:MM" se valido, altrimenti None.
    if not text:
        return None

    # Caso 1: ora + minuti
    match = TIME_PATTERN_FULL.match(text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
    else:
        # Caso 2: solo ora (es. "8" → 08:00)
        match = TIME_PATTERN_HOUR_ONLY.match(text)
        if not match:
            return None
        hour = int(match.group(1))
        minute = 0

    # Validazione range
    if not (0 <= hour <= 23):
        return None
    if not (0 <= minute <= 59):
        return None

    return f"{hour:02d}:{minute:02d}"


INVALID_TIME_MESSAGE = (
    "⏰ Non ho capito l'orario.\n\n"
    "Per favore scrivi l'orario in formato 24 ore. Esempi validi:\n"
    "• `08:30`\n"
    "• `22:15`\n\n"
)