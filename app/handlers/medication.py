# app/handlers/medication.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler

from app.db import get_db, Medication, User
from app.handlers.reminder import schedule_reminder_job
from app.utils.time_validators import parse_time, INVALID_TIME_MESSAGE
from app.utils.locales import get_text
from app.utils.dosage_validators import is_valid_dosage
from app.utils.ui import disinnesca_vecchia_tastiera, salva_id_tastiera

# Niente più SCEGLI_DESTINATARIO: il destinatario è codificato nella callback_data
NOME, DOSAGGIO, ORARIO = range(3)


async def inizia_aggiunta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Punto di ingresso. La callback_data deve essere una di:
      - inizia_aggiunta_me           → aggiungi per me stesso
      - inizia_aggiunta_<elder_id>   → aggiungi per l'assistito (solo se sono il suo curatore)
    Il vecchio 'inizia_aggiunta_btn' è anche supportato per retrocompatibilità (= per me).
    """
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get('lang', 'it')
    telegram_id = update.effective_user.id

    # Reset del destinatario all'inizio di ogni conversazione
    context.user_data.pop('destinatario_id', None)
    context.user_data.pop('destinatario_nome', None)

    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)

    # Determiniamo il destinatario dalla callback (o dal comando /aggiungi)
    callback = query.data if query else None

    if callback in (None, "inizia_aggiunta_btn", "inizia_aggiunta_me"):
        # Aggiungi per se stesso
        context.user_data['destinatario_id'] = telegram_id
        context.user_data['destinatario_nome'] = None
    else:
        # Atteso: inizia_aggiunta_<elder_id>
        try:
            elder_id = int(callback.split("_")[2])
        except (IndexError, ValueError):
            # Callback malformata: fallback su "per me"
            context.user_data['destinatario_id'] = telegram_id
            context.user_data['destinatario_nome'] = None
            return await chiedi_nome(update, context)

        # Verifica autorizzazione: il chiamante deve essere il curatore dell'elder
        db = next(get_db())
        try:
            elder = db.query(User).filter(User.telegram_id == elder_id).first()
            if not elder or elder.caregiver_telegram_id != telegram_id:
                msg = await update.effective_message.reply_text(get_text("mod_not_found", lang))
                salva_id_tastiera(context, msg.message_id)
                return ConversationHandler.END
            context.user_data['destinatario_id'] = elder_id
            context.user_data['destinatario_nome'] = elder.first_name
        finally:
            db.close()

    return await chiedi_nome(update, context)


async def chiedi_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'it')

    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)

    keyboard = [[InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="annulla_aggiunta")]]
    msg = await update.effective_message.reply_text(
        get_text("add_name", lang),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    salva_id_tastiera(context, msg.message_id)
    return NOME


async def chiedi_dosaggio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'it')
    context.user_data['nome_farmaco'] = update.message.text

    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)

    keyboard = [[InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="annulla_aggiunta")]]
    msg = await update.effective_message.reply_text(
        get_text("add_dose", lang, context.user_data['nome_farmaco']),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    salva_id_tastiera(context, msg.message_id)
    return DOSAGGIO


async def chiedi_orario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'it')
    dosaggio_input = update.message.text

    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)

    if not is_valid_dosage(dosaggio_input):
        keyboard = [[InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="annulla_aggiunta")]]
        msg = await update.effective_message.reply_text(
            get_text("invalid_dosage", lang),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        salva_id_tastiera(context, msg.message_id)
        return DOSAGGIO

    context.user_data['dosaggio'] = dosaggio_input
    keyboard = [[InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="annulla_aggiunta")]]

    msg = await update.effective_message.reply_text(
        get_text("add_time", lang),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    salva_id_tastiera(context, msg.message_id)
    return ORARIO


async def salva_farmaco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'it')
    orario_input = update.message.text
    orario = parse_time(orario_input)

    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)

    if orario is None:
        keyboard = [[InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="annulla_aggiunta")]]
        msg = await update.effective_message.reply_text(
            INVALID_TIME_MESSAGE,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        salva_id_tastiera(context, msg.message_id)
        return ORARIO

    nome = context.user_data['nome_farmaco']
    dosaggio = context.user_data['dosaggio']
    destinatario_id = context.user_data.get('destinatario_id', update.effective_user.id)
    destinatario_nome = context.user_data.get('destinatario_nome')

    db = next(get_db())
    try:
        utente = db.query(User).filter(User.telegram_id == destinatario_id).first()
        if not utente:
            utente = User(telegram_id=destinatario_id, first_name=destinatario_nome or "?", language=lang)
            db.add(utente)
            db.commit()

        nuovo_farmaco = Medication(
            user_id=destinatario_id,
            name=nome,
            dosage=dosaggio,
            time_to_take=orario,
        )
        db.add(nuovo_farmaco)
        db.commit()

        schedule_reminder_job(context.application, destinatario_id, orario)

        # "Aggiungi un altro" deve ricordare CHI è il destinatario (per non sbagliare lista)
        if destinatario_nome:
            # Aggiunto da curatore per assistito → il prossimo "aggiungi un altro" continua per l'assistito
            add_another_cb = f"inizia_aggiunta_{destinatario_id}"
            # E vediamo la lista dell'assistito, non la nostra
            view_list_cb = f"lista_assistito_{destinatario_id}"
        else:
            add_another_cb = "inizia_aggiunta_me"
            view_list_cb = "mostra_lista"

        keyboard = [
            [InlineKeyboardButton(get_text("btn_list", lang), callback_data=view_list_cb)],
            [InlineKeyboardButton(get_text("btn_add_another", lang), callback_data=add_another_cb)],
            [InlineKeyboardButton(get_text("btn_back_menu", lang), callback_data="mostra_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if destinatario_nome:
            msg = await update.effective_message.reply_text(
                get_text("add_success_for_elder", lang, destinatario_nome, nome, dosaggio, orario),
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )
        else:
            msg = await update.effective_message.reply_text(
                get_text("add_success", lang, nome, dosaggio, orario),
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )
        salva_id_tastiera(context, msg.message_id)
    finally:
        db.close()

    return ConversationHandler.END


async def annulla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = context.user_data.get('lang', 'it')
    keyboard = [[InlineKeyboardButton(get_text("btn_back_list", lang), callback_data="mostra_lista")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.answer()
        await query.edit_message_text(get_text("msg_cancelled", lang), reply_markup=reply_markup)
        salva_id_tastiera(context, query.message.message_id)
    else:
        await disinnesca_vecchia_tastiera(update.effective_chat.id, context)
        msg = await update.effective_message.reply_text(get_text("msg_cancelled", lang), reply_markup=reply_markup)
        salva_id_tastiera(context, msg.message_id)

    return ConversationHandler.END


aggiungi_farmaco_handler = ConversationHandler(
    entry_points=[
        CommandHandler('aggiungi', inizia_aggiunta),
        # Tre pattern accettati come entry: 'me', un elder ID, o il vecchio _btn (retrocompatibilità)
        CallbackQueryHandler(inizia_aggiunta, pattern=r"^inizia_aggiunta_(me|\d+|btn)$"),
    ],
    states={
        NOME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, chiedi_dosaggio),
            CallbackQueryHandler(annulla, pattern="^annulla_aggiunta$"),
        ],
        DOSAGGIO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, chiedi_orario),
            CallbackQueryHandler(annulla, pattern="^annulla_aggiunta$"),
        ],
        ORARIO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, salva_farmaco),
            CallbackQueryHandler(annulla, pattern="^annulla_aggiunta$"),
        ],
    },
    fallbacks=[
        CommandHandler('annulla', annulla),
        CallbackQueryHandler(annulla, pattern="^annulla_aggiunta$"),
    ],
)