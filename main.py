import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from app.config import TELEGRAM_BOT_TOKEN
from app.handlers import (
    start_command,
    help_command,
    mostra_menu_lingua,
    imposta_lingua_callback,
    lista_farmaci,
    lista_assistito,
    modifica_farmaco_handler,
    gestione_caregiver_menu,
    voglio_curatore,
    sono_curatore_handler,
    richiedi_rimozione,
    conferma_rimozione,
    annulla_rimozione,
)
from app.handlers.medication import aggiungi_farmaco_handler

from app.handlers.reminder import (
    confirm_medication, 
    cancel_confirm_medication, 
    really_confirm_medication, 
    confirm_all_medications, 
    cancel_confirm_all_medications, 
    really_confirm_all_medications, 
    schedule_reminder_job, 
    snooze_all_medications
)
from app.handlers.ai_leaflet import bugiardino_handler

from app.utils.logger import logger
from app.db import init_db, SessionLocal, Medication


def restore_medication_jobs(application):
    db = SessionLocal()
    try:
        medications = db.query(Medication).all()

        # Set per evitare duplicati
        scheduled = set()

        for medication in medications:
            key = (medication.user_id, medication.time_to_take)

            if key in scheduled:
                continue

            schedule_reminder_job(
                application,
                medication.user_id,
                medication.time_to_take
            )

            scheduled.add(key)

            logger.info(
                "Reminder ripristinato user=%s orario=%s",
                medication.user_id,
                medication.time_to_take
            )
    finally:
        db.close()

def main() -> None:
    init_db()
    logger.info("Starting Elder Health Assistant bot...")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Ripristina i job per tutti i farmaci esistenti
    restore_medication_jobs(app)

    # Comandi testuali (rimossi /caregiver e /iscriviti)
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("lista", lista_farmaci))

    # Conversazioni
    app.add_handler(aggiungi_farmaco_handler)
    app.add_handler(modifica_farmaco_handler)
    app.add_handler(sono_curatore_handler)   # nuovo: conversazione per il pairing
    app.add_handler(bugiardino_handler)

    # Bottoni callback
    app.add_handler(CallbackQueryHandler(lista_farmaci, pattern="^mostra_lista$"))
    app.add_handler(CallbackQueryHandler(help_command, pattern="^mostra_help$"))
    app.add_handler(CallbackQueryHandler(help_command, pattern="^menu_nuovo$")) 

    # Menu caregiver
    app.add_handler(CallbackQueryHandler(gestione_caregiver_menu, pattern="^gestisci_caregiver$"))
    app.add_handler(CallbackQueryHandler(voglio_curatore, pattern="^cg_voglio_curatore$"))
    # "Sono il curatore" è gestito dal ConversationHandler sopra

    # Lista farmaci dell'assistito (curatore)
    app.add_handler(CallbackQueryHandler(lista_assistito, pattern=r"^lista_assistito_\d+$"))

    # Rimozione con conferma
    app.add_handler(CallbackQueryHandler(richiedi_rimozione, pattern="^richiedi_rimozione$"))
    app.add_handler(CallbackQueryHandler(conferma_rimozione, pattern=r"^conferma_rimozione_\d+$"))
    app.add_handler(CallbackQueryHandler(annulla_rimozione, pattern=r"^annulla_rimozione_\d+$"))

    # Lingua
    app.add_handler(CallbackQueryHandler(mostra_menu_lingua, pattern="^mostra_menu_lingua$"))
    app.add_handler(CallbackQueryHandler(imposta_lingua_callback, pattern="^set_lang_(it|en)$"))

    # Reminder (Flusso di Doppia Conferma)
    app.add_handler(CallbackQueryHandler(confirm_all_medications, pattern=r"^confirm_all_"))
    app.add_handler(CallbackQueryHandler(cancel_confirm_all_medications, pattern=r"^cancel_confirm_all_"))
    app.add_handler(CallbackQueryHandler(really_confirm_all_medications, pattern=r"^really_confirm_all_"))

    app.add_handler(CallbackQueryHandler(confirm_medication, pattern=r"^confirm_\d+$"))
    app.add_handler(CallbackQueryHandler(cancel_confirm_medication, pattern=r"^cancel_confirm_\d+$"))
    app.add_handler(CallbackQueryHandler(really_confirm_medication, pattern=r"^really_confirm_\d+$"))
    
    app.add_handler(CallbackQueryHandler(snooze_all_medications, pattern=r"^snooze_all_"))

    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    try:
        main()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        main()