# app/handlers/start.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.db import get_db, User
from app.utils.locales import get_text
from app.utils.ui import disinnesca_vecchia_tastiera, salva_id_tastiera

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user
    db = next(get_db())
    
    try:
        db_user = db.query(User).filter(User.telegram_id == telegram_user.id).first()
        
        if not db_user:
            db_user = User(
                telegram_id=telegram_user.id, 
                first_name=telegram_user.first_name
            )
            db.add(db_user)
            db.commit()
            print(f"✅ Nuovo utente registrato nel DB: {telegram_user.first_name}")
            
        lang = db_user.language
        context.user_data['lang'] = lang
            
    finally:
        db.close()

    # Disinneschiamo eventuale menu rimasto aperto prima del riavvio
    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)

    keyboard = [
        [InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="mostra_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    messaggio_benvenuto = get_text("start_welcome", lang, telegram_user.first_name)
    
    msg = await update.message.reply_text(messaggio_benvenuto, reply_markup=reply_markup)
    
    salva_id_tastiera(context, msg.message_id)