import os
import asyncio
from pathlib import Path
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv

from app.db import init_db

# 1. PREPARIAMO L'AMBIENTE PER PRIMA COSA
base_path = Path(__file__).resolve().parent
env_path = base_path / ".env"
load_dotenv(dotenv_path=env_path)

# --- INIZIALIZZA IL DATABASE ---
init_db()
# -------------------------------

# 2. ORA IMPORTIAMO I FILE DEL BOT
from app.handlers import start_command, help_command, lista_farmaci, modifica_farmaco_handler
from app.handlers.medication import aggiungi_farmaco_handler
from app.handlers.reminder import confirm_medication

from app.config import TELEGRAM_BOT_TOKEN

# Inizializziamo l'app web Flask
app = Flask(__name__)

# Inizializziamo l'app Telegram
bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
bot_app.add_handler(CommandHandler("start", start_command))
bot_app.add_handler(CommandHandler("help", help_command))
bot_app.add_handler(CommandHandler("lista", lista_farmaci))

# Gestori delle conversazioni
bot_app.add_handler(aggiungi_farmaco_handler)
bot_app.add_handler(modifica_farmaco_handler)

# Gestori dei bottoni fissi
bot_app.add_handler(CallbackQueryHandler(lista_farmaci, pattern="^mostra_lista$"))
bot_app.add_handler(CallbackQueryHandler(help_command, pattern="^mostra_help$"))

# Gestore dei reminder
bot_app.add_handler(CallbackQueryHandler(confirm_medication, pattern=r"^confirm_\d+$"))

# Rotta di base per verificare che il server sia acceso
@app.route('/')
def home():
    return "L'Elder Health Assistant è online 24/7!"

# Sostituisci la tua funzione webhook con questa:

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.method == "POST":
        try:
            json_data = request.get_json(force=True)
            update = Update.de_json(json_data, bot_app.bot)

            # Cerchiamo di ottenere il loop corrente o ne creiamo uno
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Inizializzazione sicura
            if not bot_app._initialized:
                loop.run_until_complete(bot_app.initialize())
            
            # Eseguiamo l'update
            loop.run_until_complete(bot_app.process_update(update))

            return "OK", 200
        except Exception as e:
            print(f"Errore nel Webhook: {e}")
            return "Error", 500