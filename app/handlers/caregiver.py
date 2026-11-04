# app/handlers/caregiver.py
import secrets
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from app.db import get_db, User
from app.utils.logger import logger
from app.utils.locales import get_text
from app.utils.ui import disinnesca_vecchia_tastiera, salva_id_tastiera # IMPORT

CG_ATTESA_CODICE = 0

def _generate_token() -> str:
    alphabet = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(alphabet) for _ in range(6))

def _get_role(db, telegram_id: int) -> tuple[str, User | None]:
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user and user.caregiver_telegram_id:
        cg = db.query(User).filter(User.telegram_id == user.caregiver_telegram_id).first()
        return "elder", cg

    assisted = db.query(User).filter(User.caregiver_telegram_id == telegram_id).first()
    if assisted:
        return "caregiver", assisted

    return "none", None

async def gestione_caregiver_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get('lang', 'it')
    telegram_id = update.effective_user.id
    first_name = update.effective_user.first_name

    # Disinneschiamo il menu precedente (Nuova Schermata)
    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)

    db = next(get_db())
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id, first_name=first_name, language=lang)
            db.add(user)
            db.commit()

        role, other = _get_role(db, telegram_id)

        if role == "elder":
            text = get_text("cg_elder_status", lang, other.first_name if other else "?")
            keyboard = [
                [InlineKeyboardButton(get_text("btn_rimuovi_curatore", lang), callback_data="richiedi_rimozione")],
                [InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="mostra_help")],
            ]
        elif role == "caregiver":
            text = get_text("cg_caregiver_status", lang, other.first_name if other else "?")
            keyboard = [
                [InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="mostra_help")],
            ]
        else:
            text = get_text("cg_menu_title_neutral", lang)
            keyboard = [
                [InlineKeyboardButton(get_text("btn_sono_curatore", lang), callback_data="cg_sono_curatore")],
                [InlineKeyboardButton(get_text("btn_voglio_curatore", lang), callback_data="cg_voglio_curatore")],
                [InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="mostra_help")],
            ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        
        msg = await update.effective_message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)
        salva_id_tastiera(context, msg.message_id)

    finally:
        db.close()

async def voglio_curatore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get('lang', 'it')
    telegram_id = update.effective_user.id

    # Disinneschiamo il menu precedente
    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)

    db = next(get_db())
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        role, other = _get_role(db, telegram_id)
        if role == "caregiver":
            msg = await update.effective_message.reply_text(
                get_text("cg_role_taken_caregiver", lang, other.first_name if other else "?"),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="mostra_help")
                ]]),
            )
            salva_id_tastiera(context, msg.message_id)
            return

        token = _generate_token()
        user.pairing_token = token
        db.commit()

        keyboard = [[InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="mostra_help")]]
        msg = await update.effective_message.reply_text(
            get_text("cg_connect_setup", lang, token),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        context.application.bot_data.setdefault('pairing_msg_ids', {})[telegram_id] = msg.message_id
        salva_id_tastiera(context, msg.message_id)

    finally:
        db.close()

async def sono_curatore_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'it')
    telegram_id = update.effective_user.id

    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)

    db = next(get_db())
    try:
        role, other = _get_role(db, telegram_id)
        if role == "elder":
            msg = await update.effective_message.reply_text(
                get_text("cg_role_taken_elder", lang),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="mostra_help")
                ]]),
            )
            salva_id_tastiera(context, msg.message_id)
            return ConversationHandler.END

        if role == "caregiver":
            msg = await update.effective_message.reply_text(
                get_text("cg_role_taken_caregiver", lang, other.first_name if other else "?"),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="mostra_help")
                ]]),
            )
            salva_id_tastiera(context, msg.message_id)
            return ConversationHandler.END
    finally:
        db.close()

    keyboard = [[InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="annulla_codice")]]
    msg = await update.effective_message.reply_text(
        get_text("cg_ask_code", lang),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    salva_id_tastiera(context, msg.message_id)
    return CG_ATTESA_CODICE

async def sono_curatore_riceve_codice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'it')
    caregiver_id = update.effective_user.id
    caregiver_name = update.effective_user.first_name
    token = update.message.text.strip().upper()

    # L'utente ha digitato testo. Disinneschiamo la domanda precedente!
    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)

    db = next(get_db())
    try:
        role, other = _get_role(db, caregiver_id)
        if role != "none":
            msg = await update.effective_message.reply_text(
                get_text("cg_role_taken_caregiver", lang, other.first_name) if role == "caregiver"
                else get_text("cg_role_taken_elder", lang),
                parse_mode="Markdown",
            )
            salva_id_tastiera(context, msg.message_id)
            return ConversationHandler.END

        elder = db.query(User).filter(User.pairing_token == token).first()

        if not elder:
            keyboard = [[InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="annulla_codice")]]
            msg = await update.effective_message.reply_text(
                get_text("cg_invalid_token", lang),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            salva_id_tastiera(context, msg.message_id)
            return CG_ATTESA_CODICE

        if elder.telegram_id == caregiver_id:
            keyboard = [[InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="annulla_codice")]]
            msg = await update.effective_message.reply_text(
                get_text("cg_self_pairing", lang),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            salva_id_tastiera(context, msg.message_id)
            return CG_ATTESA_CODICE

        elder_role, _ = _get_role(db, elder.telegram_id)
        if elder_role == "caregiver":
            msg = await update.effective_message.reply_text(get_text("cg_invalid_token", lang))
            salva_id_tastiera(context, msg.message_id)
            return CG_ATTESA_CODICE

        elder.caregiver_telegram_id = caregiver_id
        elder.pairing_token = None
        db.commit()

        cg_user = db.query(User).filter(User.telegram_id == caregiver_id).first()
        if not cg_user:
            cg_user = User(telegram_id=caregiver_id, first_name=caregiver_name, language=lang)
            db.add(cg_user)
            db.commit()
        cg_lang = cg_user.language if cg_user.language else lang

        msg = await update.effective_message.reply_text(
            get_text("cg_caregiver_success", cg_lang, elder.first_name),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text("btn_main_menu", cg_lang), callback_data="mostra_help")
            ]]),
        )
        salva_id_tastiera(context, msg.message_id)

        pairing_msg_ids = context.application.bot_data.get('pairing_msg_ids', {})
        old_msg_id = pairing_msg_ids.pop(elder.telegram_id, None)
        if old_msg_id:
            try:
                await context.bot.delete_message(chat_id=elder.telegram_id, message_id=old_msg_id)
            except Exception:
                pass

        elder_lang = elder.language if elder.language else "it"
        try:
            await context.bot.send_message(
                chat_id=elder.telegram_id,
                text=get_text("cg_elder_notification", elder_lang, caregiver_name),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text("btn_main_menu", elder_lang), callback_data="mostra_help")
                ]]),
            )
        except Exception:
            pass
        
        return ConversationHandler.END

    finally:
        db.close()

async def annulla_codice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = context.user_data.get('lang', 'it')
    if query:
        await query.answer()
        # Modifica interna (Azione)
        await query.edit_message_text(
            get_text("msg_cancelled", lang),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="mostra_help")
            ]]),
        )
        salva_id_tastiera(context, query.message.message_id)
    else:
        await disinnesca_vecchia_tastiera(update.effective_chat.id, context)
        msg = await update.effective_message.reply_text(get_text("msg_cancelled", lang))
        salva_id_tastiera(context, msg.message_id)
    return ConversationHandler.END

async def richiedi_rimozione(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get('lang', 'it')
    telegram_id = update.effective_user.id
    first_name = update.effective_user.first_name

    db = next(get_db())
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user or not user.caregiver_telegram_id:
            await query.edit_message_text(get_text("cg_no_cg_to_remove", lang))
            salva_id_tastiera(context, query.message.message_id)
            return

        caregiver_id = user.caregiver_telegram_id
        cg_user = db.query(User).filter(User.telegram_id == caregiver_id).first()
        cg_lang = cg_user.language if cg_user and cg_user.language else "it"

        keyboard = [
            [InlineKeyboardButton(
                get_text("btn_conferma_rimozione", cg_lang),
                callback_data=f"conferma_rimozione_{telegram_id}"
            )],
            [InlineKeyboardButton(
                get_text("btn_annulla_rimozione", cg_lang),
                callback_data=f"annulla_rimozione_{telegram_id}"
            )],
        ]

        try:
            await context.bot.send_message(
                chat_id=caregiver_id,
                text=get_text("cg_removal_request_to_cg", cg_lang, first_name),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        except Exception:
            await query.edit_message_text(get_text("leaf_error", lang))
            salva_id_tastiera(context, query.message.message_id)
            return

        cg_name = cg_user.first_name if cg_user else "?"
        # Azione rapida su se stesso
        await query.edit_message_text(
            get_text("cg_removal_requested_elder", lang, cg_name),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="mostra_help")
            ]]),
        )
        salva_id_tastiera(context, query.message.message_id)

    finally:
        db.close()

async def conferma_rimozione(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get('lang', 'it')
    caregiver_id = update.effective_user.id
    caregiver_name = update.effective_user.first_name

    try:
        elder_id = int(query.data.split("_")[2])
    except (IndexError, ValueError):
        await query.edit_message_text(get_text("cg_no_pending_removal", lang))
        salva_id_tastiera(context, query.message.message_id)
        return

    db = next(get_db())
    try:
        elder = db.query(User).filter(User.telegram_id == elder_id).first()
        if not elder or elder.caregiver_telegram_id != caregiver_id:
            await query.edit_message_text(get_text("cg_no_pending_removal", lang))
            salva_id_tastiera(context, query.message.message_id)
            return

        elder.caregiver_telegram_id = None
        db.commit()

        # Edit sul messaggio di notifica del caregiver
        await query.edit_message_text(
            get_text("cg_removal_confirmed_cg", lang, elder.first_name),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="mostra_help")
            ]]),
        )
        salva_id_tastiera(context, query.message.message_id)

        elder_lang = elder.language if elder.language else "it"
        try:
            await context.bot.send_message(
                chat_id=elder_id,
                text=get_text("cg_removal_confirmed_elder", elder_lang, caregiver_name),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text("btn_main_menu", elder_lang), callback_data="mostra_help")
                ]]),
            )
        except Exception:
            pass

    finally:
        db.close()

async def annulla_rimozione(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get('lang', 'it')
    caregiver_name = update.effective_user.first_name

    try:
        elder_id = int(query.data.split("_")[2])
    except (IndexError, ValueError):
        await query.edit_message_text(get_text("cg_no_pending_removal", lang))
        salva_id_tastiera(context, query.message.message_id)
        return

    db = next(get_db())
    try:
        elder = db.query(User).filter(User.telegram_id == elder_id).first()
        if not elder:
            await query.edit_message_text(get_text("cg_no_pending_removal", lang))
            salva_id_tastiera(context, query.message.message_id)
            return

        # Edit sul messaggio di notifica del caregiver
        await query.edit_message_text(
            get_text("cg_removal_cancelled_cg", lang, elder.first_name),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="mostra_help")
            ]]),
        )
        salva_id_tastiera(context, query.message.message_id)

        elder_lang = elder.language if elder.language else "it"
        try:
            await context.bot.send_message(
                chat_id=elder_id,
                text=get_text("cg_removal_cancelled_elder", elder_lang, caregiver_name),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text("btn_main_menu", elder_lang), callback_data="mostra_help")
                ]]),
            )
        except Exception:
            pass

    finally:
        db.close()

sono_curatore_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(sono_curatore_start, pattern="^cg_sono_curatore$")
    ],
    states={
        CG_ATTESA_CODICE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, sono_curatore_riceve_codice),
            CallbackQueryHandler(annulla_codice, pattern="^annulla_codice$"),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(annulla_codice, pattern="^annulla_codice$"),
    ],
)