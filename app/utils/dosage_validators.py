"""Validatore per il dosaggio dei farmaci."""
import re

# Deve contenere almeno una cifra. Accetta: "2", "2g", "2 pillole", "500mg", "1/2", "10 ml"
# Rifiuta: "mm", "abc", "11:47" (orario, niente unità sensata) — vedi nota sotto
_HAS_DIGIT = re.compile(r"\d")
# Rifiuta input che sembra un orario (es. "11:47", "8:30") per evitare confusione col campo orario
_LOOKS_LIKE_TIME = re.compile(r"^\s*\d{1,2}\s*[:.\-h]\s*\d{2}\s*$")


def is_valid_dosage(text: str) -> bool:
    """
    Ritorna True se il dosaggio sembra valido.
    Regola: deve contenere almeno una cifra e non deve essere un orario.
    """
    if not text or not text.strip():
        return False
    if _LOOKS_LIKE_TIME.match(text):
        return False
    if not _HAS_DIGIT.search(text):
        return False
    return True