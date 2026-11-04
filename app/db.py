from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from pathlib import Path
from datetime import datetime

# Definiamo il percorso dove verrà salvato il file del database
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "elder_assistant.db"

# Creiamo il "motore" del database SQLite
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# Creiamo la classe base da cui deriveranno i nostri modelli
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- MODELLI DEL DATABASE ---

class User(Base):
    """Tabella per memorizzare gli utenti"""
    __tablename__ = "users"

    telegram_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=True)

    # --- NUOVA COLONNA LINGUA ---
    # Impostiamo l'italiano ("it") come lingua di default per tutti i nuovi utenti
    language = Column(String, default="it")

    # Dati caregiver
    caregiver_telegram_id = Column(Integer, nullable=True)
    pairing_token = Column(String, nullable=True, unique=True)
    
    # Relazione: un utente ha molti farmaci
    medications = relationship("Medication", back_populates="user", cascade="all, delete-orphan")


class Medication(Base):
    """Tabella per memorizzare la routine dei farmaci"""
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    
    name = Column(String, nullable=False)        # Es: "Cardioaspirina"
    dosage = Column(String, nullable=True)       # Es: "1 pillola"
    time_to_take = Column(String, nullable=False) # Es: "08:00"

    # Relazione: il farmaco appartiene a un utente
    user = relationship("User", back_populates="medications")

class MedicationLog(Base):
    """Storico reminder e conferme assunzione"""
    __tablename__ = "medication_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False)
    scheduled_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    confirmed = Column(Boolean, default=False)
    confirmed_at = Column(DateTime, nullable=True)
    caregiver_notified = Column(Boolean, default=False)

    medication = relationship("Medication")

# --- FUNZIONI DI SUPPORTO ---

def init_db():
    """Crea le tabelle nel database se non esistono già"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Fornisce una sessione del database da usare nel codice"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()