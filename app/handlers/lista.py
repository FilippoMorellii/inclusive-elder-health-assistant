# app/handlers/lista.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.db import get_db, Medication, User
from app.utils.locales import get_text
from app.utils.ui import disinnesca_vecchia_tastiera, salva_id_tastiera


async def lista_farmaci(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista dei farmaci dell'utente stesso. 'Aggiungi' aggiunge SEMPRE a se stessi."""
    query = update.callback_query
    if query:
        await query.answer()

    telegram_id = update.effective_user.id
    lang = context.user_data.get('lang', 'it')

    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)

    db = next(get_db())
    try:
        farmaci = db.query(Medication).filter(Medication.user_id == telegram_id).all()

        if not farmaci:
            keyboard = [
                # 'Aggiungi' qui è SEMPRE per me
                [InlineKeyboardButton(get_text("btn_add_first", lang), callback_data="inizia_aggiunta_me")],
                [InlineKeyboardButton(get_text("btn_back_menu", lang), callback_data="mostra_help")]
            ]
            msg = await update.effective_message.reply_text(
                get_text("empty_list", lang),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            salva_id_tastiera(context, msg.message_id)
            return

        messaggio = get_text("list_title", lang)
        for f in farmaci:
            messaggio += f"🔸 *{f.name}*\n   {get_text('btn_dosage', lang)}: {f.dosage}\n   {get_text('btn_time', lang)}: {f.time_to_take}\n\n"

        keyboard = [
            [InlineKeyboardButton(get_text("btn_edit_delete", lang), callback_data="inizia_modifica")],
            # 'Aggiungi' qui è SEMPRE per me
            [InlineKeyboardButton(get_text("btn_add_another", lang), callback_data="inizia_aggiunta_me")],
            [InlineKeyboardButton(get_text("btn_back_menu", lang), callback_data="mostra_help")]
        ]

        msg = await update.effective_message.reply_text(
            messaggio,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        salva_id_tastiera(context, msg.message_id)

    finally:
        db.close()


async def lista_assistito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista dei farmaci dell'assistito (vista dal curatore).
    'Aggiungi' qui aggiunge SEMPRE per l'assistito."""
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get('lang', 'it')
    caregiver_id = update.effective_user.id

    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)

    # callback_data: lista_assistito_<elder_id>
    try:
        elder_id = int(query.data.split("_")[2])
    except (IndexError, ValueError, AttributeError):
        await update.effective_message.reply_text(get_text("mod_not_found", lang))
        return

    db = next(get_db())
    try:
        # Verifica autorizzazione
        elder = db.query(User).filter(User.telegram_id == elder_id).first()
        if not elder or elder.caregiver_telegram_id != caregiver_id:
            await update.effective_message.reply_text(get_text("mod_not_found", lang))
            return

        farmaci = db.query(Medication).filter(Medication.user_id == elder_id).all()

        if not farmaci:
            keyboard = [
                # 'Aggiungi' qui aggiunge per l'assistito (carry-encoding nell'ID callback)
                [InlineKeyboardButton(
                    get_text("btn_add_first", lang),
                    callback_data=f"inizia_aggiunta_{elder_id}"
                )],
                [InlineKeyboardButton(get_text("btn_back_menu", lang), callback_data="mostra_help")]
            ]
            msg = await update.effective_message.reply_text(
                get_text("empty_list_assistito", lang, elder.first_name),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            salva_id_tastiera(context, msg.message_id)
            return

        messaggio = get_text("list_title_assistito", lang, elder.first_name)
        for f in farmaci:
            messaggio += f"🔸 *{f.name}*\n   {get_text('btn_dosage', lang)}: {f.dosage}\n   {get_text('btn_time', lang)}: {f.time_to_take}\n\n"

        keyboard = [
            # 'Aggiungi' qui aggiunge per l'assistito
            [InlineKeyboardButton(
                get_text("btn_add_another", lang),
                callback_data=f"inizia_aggiunta_{elder_id}"
            )],
            [InlineKeyboardButton(get_text("btn_back_menu", lang), callback_data="mostra_help")]
        ]

        msg = await update.effective_message.reply_text(
            messaggio,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        salva_id_tastiera(context, msg.message_id)

    finally:
        db.close()