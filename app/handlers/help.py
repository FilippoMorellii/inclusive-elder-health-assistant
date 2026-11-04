# app/handlers/help.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.db import get_db, Medication, User
from app.utils.locales import get_text
from app.utils.ui import disinnesca_vecchia_tastiera, salva_id_tastiera # IMPORT

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mostra il menu principale dinamico come nuovo messaggio e disinnesca il vecchio."""
    query = update.callback_query
    if query:
        await query.answer()

    telegram_id = update.effective_user.id
    db = next(get_db())
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        lang = user.language if user else "it"
        context.user_data['lang'] = lang

        assisted = db.query(User).filter(User.caregiver_telegram_id == telegram_id).first()
    finally:
        db.close()

    text = get_text("menu_title", lang)
    keyboard = []

    keyboard.append([InlineKeyboardButton(get_text("btn_list", lang), callback_data="mostra_lista")])

    if assisted:
        keyboard.append([InlineKeyboardButton(
            get_text("btn_lista_assistito", lang, assisted.first_name),
            callback_data=f"lista_assistito_{assisted.telegram_id}"
        )])

    keyboard.append([InlineKeyboardButton(get_text("btn_leaflet", lang), callback_data="inizia_bugiardino")])
    keyboard.append([InlineKeyboardButton(get_text("btn_caregiver", lang), callback_data="gestisci_caregiver")])
    keyboard.append([InlineKeyboardButton(get_text("btn_language", lang), callback_data="mostra_menu_lingua")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # 1. Disinneschiamo sempre la vecchia tastiera attiva
    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)
            
    # 2. Inviamo il nuovo menu in fondo alla chat
    msg = await update.effective_message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    
    # 3. Salviamo l'ID del nuovo messaggio
    salva_id_tastiera(context, msg.message_id)


async def mostra_menu_lingua(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sottomenu di scelta esplicita della lingua (Modifica il messaggio esistente)."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'it')

    text = get_text("lang_menu_title", lang)
    keyboard = [
        [InlineKeyboardButton("🇮🇹 Italiano", callback_data="set_lang_it")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en")],
        [InlineKeyboardButton(get_text("btn_back", lang), callback_data="mostra_help")]
    ]
    # Essendo una "modifica" / "sottomenu", continuiamo a usare edit_message_text
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    salva_id_tastiera(context, query.message.message_id)


async def imposta_lingua_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Salva la lingua scelta e ricarica il menu."""
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id
    nuova_lingua = "it" if query.data == "set_lang_it" else "en"

    db = next(get_db())
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            user.language = nuova_lingua
            db.commit()
    finally:
        db.close()

    context.user_data['lang'] = nuova_lingua
    
    # Rilanciamo il comando help (che ora genererà un nuovo messaggio disinnescando questo)
    await help_command(update, context)