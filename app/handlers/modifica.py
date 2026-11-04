# app/handlers/modifica.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from app.db import get_db, Medication
from app.utils.time_validators import parse_time, INVALID_TIME_MESSAGE
from app.handlers.reminder import (
    schedule_reminder_job,
    remove_reminder_job
)
from app.utils.locales import get_text
from app.utils.ui import disinnesca_vecchia_tastiera, salva_id_tastiera # IMPORT

SELEZIONA_FARMACO, SCEGLI_CAMPO_MOD, MODIFICA_SINGOLA = range(3)

def rebuild_reminder_for_time(application, db, user_id, medication_time):
    remove_reminder_job(application, user_id, medication_time)
    remaining = db.query(Medication).filter(
        Medication.user_id == user_id,
        Medication.time_to_take == medication_time
    ).count()
    if remaining > 0:
        schedule_reminder_job(application, user_id, medication_time)

def get_nav_keyboard(lang: str):
    return InlineKeyboardMarkup([[InlineKeyboardButton(get_text("btn_back_list", lang), callback_data="mostra_lista")]])

async def inizia_modifica(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query: await query.answer()

    lang = context.user_data.get('lang', 'it')
    telegram_id = update.effective_user.id
    
    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)
    
    db = next(get_db())
    try:
        farmaci = db.query(Medication).filter(Medication.user_id == telegram_id).all()
        if not farmaci:
            # Senza tastiera, non c'è da salvare id_tastiera
            await update.effective_message.reply_text(get_text("mod_no_meds", lang))
            return ConversationHandler.END

        keyboard = []
        for f in farmaci:
            keyboard.append([InlineKeyboardButton(f"💊 {f.name} ({f.time_to_take})", callback_data=f"sel_{f.id}")])
        keyboard.append([InlineKeyboardButton(get_text("btn_back", lang), callback_data="annulla_mod")])

        msg = await update.effective_message.reply_text(get_text("mod_select", lang), reply_markup=InlineKeyboardMarkup(keyboard))
        salva_id_tastiera(context, msg.message_id)
        return SELEZIONA_FARMACO
    finally:
        db.close()

async def mostra_opzioni_farmaco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'it')

    if query.data == "annulla_mod":
        await query.edit_message_text(get_text("msg_cancelled", lang), reply_markup=get_nav_keyboard(lang))
        salva_id_tastiera(context, query.message.message_id)
        return ConversationHandler.END
    
    farmaco_id = int(query.data.split("_")[1])
    context.user_data['mod_id'] = farmaco_id

    db = next(get_db())
    try:
        farmaco = db.query(Medication).filter(Medication.id == farmaco_id).first()
        if not farmaco:
            await query.edit_message_text(get_text("mod_not_found", lang), reply_markup=get_nav_keyboard(lang))
            salva_id_tastiera(context, query.message.message_id)
            return ConversationHandler.END

        nome_lbl = "Nome" if lang == "it" else "Name"
        orario_lbl = "Orario" if lang == "it" else "Time"
        testo_base = (
            f"💊 *{farmaco.name}*\n"
            f"🔸 {nome_lbl}: {farmaco.name}\n"
            f"🔸 Dose: {farmaco.dosage}\n"
            f"🔸 {orario_lbl}: {farmaco.time_to_take}\n"
        )
        context.user_data['dettagli_farmaco_testo'] = testo_base
        testo_schermata = f"{testo_base}\n{get_text('mod_what_to_edit', lang)}"

        keyboard = [
            [InlineKeyboardButton(get_text("btn_mod_name", lang), callback_data="mod_nome")],
            [InlineKeyboardButton(get_text("btn_mod_dose", lang), callback_data="mod_dose")],
            [InlineKeyboardButton(get_text("btn_mod_time", lang), callback_data="mod_orario")],
            [InlineKeyboardButton(get_text("btn_delete", lang), callback_data="scegli_elimina")],
            [InlineKeyboardButton(get_text("btn_back", lang), callback_data="annulla_mod")]
        ]
        
        await query.edit_message_text(text=testo_schermata, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        salva_id_tastiera(context, query.message.message_id)
        return SCEGLI_CAMPO_MOD
    finally:
        db.close()

async def chiedi_nuovo_valore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'it')

    if query.data == "annulla_mod":
        await query.edit_message_text(get_text("msg_cancelled", lang), reply_markup=get_nav_keyboard(lang))
        salva_id_tastiera(context, query.message.message_id)
        return ConversationHandler.END

    azione = query.data

    if azione == "scegli_elimina":
        farmaco_id = context.user_data['mod_id']
        db = next(get_db())

        try:
            farmaco = db.query(Medication).filter(Medication.id == farmaco_id).first()
            if farmaco:
                nome = farmaco.name
                user_id = farmaco.user_id
                old_time = farmaco.time_to_take

                db.delete(farmaco)
                db.commit()

                rebuild_reminder_for_time(context.application, db, user_id, old_time)

                await query.edit_message_text(text=get_text("delete_success", lang, nome), parse_mode="Markdown", reply_markup=get_nav_keyboard(lang))
                salva_id_tastiera(context, query.message.message_id)
        finally:
            db.close()
        return ConversationHandler.END

    context.user_data['campo_da_modificare'] = azione
    messaggi_richiesta = {
        "mod_nome": get_text("ask_new_name", lang),
        "mod_dose": get_text("ask_new_dose", lang),
        "mod_orario": get_text("ask_new_time", lang)
    }

    testo_base = context.user_data.get('dettagli_farmaco_testo', '')
    testo_finale = f"{testo_base}\n{messaggi_richiesta[azione]}"
    keyboard = [[InlineKeyboardButton(get_text("btn_back", lang), callback_data="annulla_mod")]]
    
    await query.edit_message_text(text=testo_finale, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    salva_id_tastiera(context, query.message.message_id)
    return MODIFICA_SINGOLA

async def salva_modifica_singola(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'it')
    nuovo_valore = update.message.text
    campo = context.user_data['campo_da_modificare']
    farmaco_id = context.user_data['mod_id']

    # Testo digitato dall'utente! Nuova risposta = spegniamo la tastiera della domanda precedente
    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)

    if campo == "mod_orario":
        nuovo_valore = parse_time(nuovo_valore)
        if nuovo_valore is None:
            keyboard = [[InlineKeyboardButton(get_text("btn_back", lang), callback_data="annulla_mod")]]
            msg = await update.effective_message.reply_text(INVALID_TIME_MESSAGE, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
            salva_id_tastiera(context, msg.message_id)
            return MODIFICA_SINGOLA

    db = next(get_db())
    try:
        farmaco = db.query(Medication).filter(Medication.id == farmaco_id).first()
        if farmaco:

            old_time = farmaco.time_to_take
            user_id = farmaco.user_id

            if campo == "mod_nome": farmaco.name = nuovo_valore
            elif campo == "mod_dose": farmaco.dosage = nuovo_valore
            elif campo == "mod_orario": farmaco.time_to_take = nuovo_valore

            db.commit()
            
            rebuild_reminder_for_time(context.application, db, user_id, old_time)
            rebuild_reminder_for_time(context.application, db, user_id, farmaco.time_to_take)

            msg = await update.message.reply_text(get_text("mod_success", lang, farmaco.name), parse_mode="Markdown", reply_markup=get_nav_keyboard(lang))
            salva_id_tastiera(context, msg.message_id)
    finally:
        db.close()
    return ConversationHandler.END

async def annulla_modifica(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = context.user_data.get('lang', 'it')
    if query: 
        await query.answer()
        await query.edit_message_text(get_text("msg_cancelled", lang), reply_markup=get_nav_keyboard(lang))
        salva_id_tastiera(context, query.message.message_id)
    else:
        await disinnesca_vecchia_tastiera(update.effective_chat.id, context)
        msg = await update.effective_message.reply_text(get_text("msg_cancelled", lang), reply_markup=get_nav_keyboard(lang))
        salva_id_tastiera(context, msg.message_id)
    return ConversationHandler.END

# (Il blocco handler modifica_farmaco_handler rimane invariato)
modifica_farmaco_handler = ConversationHandler(
    entry_points=[
        CommandHandler('modifica', inizia_modifica),
        CallbackQueryHandler(inizia_modifica, pattern="^inizia_modifica$")
    ],
    states={
        SELEZIONA_FARMACO: [CallbackQueryHandler(mostra_opzioni_farmaco, pattern="^(sel_|annulla_mod)")],
        SCEGLI_CAMPO_MOD: [CallbackQueryHandler(chiedi_nuovo_valore, pattern="^(mod_nome|mod_dose|mod_orario|scegli_elimina|annulla_mod)")],
        MODIFICA_SINGOLA: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, salva_modifica_singola),
            CallbackQueryHandler(annulla_modifica, pattern="^annulla_mod$")
        ],
    },
    fallbacks=[
        CommandHandler('annulla', annulla_modifica),
        CallbackQueryHandler(annulla_modifica, pattern="^annulla_mod$")
    ]
)