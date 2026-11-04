# app/handlers/reminder.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from datetime import datetime
from time import time as timestamp_time
from datetime import timedelta, time
from zoneinfo import ZoneInfo

from app.db import SessionLocal, MedicationLog, User, Medication
from app.config import CAREGIVER_TIMEOUT_MINUTES, REMINDER_SNOOZE_MINUTES
from app.utils.logger import logger
from app.utils.locales import get_text
from app.utils.ui import disinnesca_vecchia_tastiera, salva_id_tastiera

def build_reminder_job_name(user_id, medication_time):
    safe_time = medication_time.replace(":", "_")
    return f"reminder_{user_id}_{safe_time}"

def remove_reminder_job(application, user_id, medication_time):
    job_name = build_reminder_job_name(user_id, medication_time)
    current_jobs = application.job_queue.get_jobs_by_name(job_name)
    for job in current_jobs:
        job.schedule_removal()

def schedule_reminder_job(application, user_id, medication_time):
    from datetime import time
    from zoneinfo import ZoneInfo

    hour, minute = map(int, medication_time.split(":"))
    job_name = build_reminder_job_name(user_id, medication_time)

    existing_jobs = application.job_queue.get_jobs_by_name(job_name)
    if existing_jobs:
        return

    application.job_queue.run_daily(
        send_medication_reminder,
        time=time(hour=hour, minute=minute, tzinfo=ZoneInfo("Europe/Rome")),
        data={"user_id": user_id, "medication_time": medication_time},
        name=job_name,
        chat_id=user_id,
        user_id=user_id
    )

async def send_medication_reminder(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.data
    user_id = job_data["user_id"]
    medication_time = job_data["medication_time"]

    db = SessionLocal()
    scheduled_dt = datetime.now(ZoneInfo("Europe/Rome"))

    try:
        elder = db.query(User).filter(User.telegram_id == user_id).first()
        if not elder: return
        elder_lang = elder.language if elder else "it"

        medications = db.query(Medication).filter(
            Medication.user_id == user_id,
            Medication.time_to_take == medication_time
        ).all()

        if not medications: return

        logs = []
        for medication in medications:
            log = MedicationLog(medication_id=medication.id, scheduled_time=scheduled_dt)
            db.add(log)
            db.commit()
            db.refresh(log)
            logs.append({"log": log, "medication": medication})

        text = get_text("rem_multi_title", elder_lang)
        for item in logs:
            medication = item["medication"]
            text += get_text("rem_med_line", elder_lang, medication.name, medication.dosage)

        keyboard = []
        for item in logs:
            log = item["log"]
            medication = item["medication"]
            keyboard.append([InlineKeyboardButton(f"✅ {medication.name}", callback_data=f"confirm_{log.id}")])

        all_log_ids = ",".join(str(item["log"].id) for item in logs)
        
        if len(logs) > 1:
            keyboard.append([InlineKeyboardButton(get_text("btn_confirm_all", elder_lang), callback_data=f"confirm_all_{all_log_ids}")])
            
        keyboard.append([InlineKeyboardButton(get_text("btn_snooze", elder_lang, REMINDER_SNOOZE_MINUTES), callback_data=f"snooze_all_{all_log_ids}")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await disinnesca_vecchia_tastiera(user_id, context)

        msg = await context.bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        salva_id_tastiera(context, msg.message_id)

        for item in logs:
            log = item["log"]
            medication = item["medication"]
            context.application.job_queue.run_once(
                check_confirmation_and_notify_caregiver,
                when=CAREGIVER_TIMEOUT_MINUTES * 60,
                data={
                    "log_id": log.id,
                    "elder_chat_id": user_id,
                    "medication_name": medication.name,
                    "dosage": medication.dosage,
                },
                name=f"escalation_{log.id}",
                chat_id=user_id,
                user_id=user_id
            )
    finally:
        db.close()

async def check_confirmation_and_notify_caregiver(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.data
    log_id = job_data["log_id"]
    elder_chat_id = job_data["elder_chat_id"]
    medication_name = job_data["medication_name"]
    dosage = job_data["dosage"]

    db = SessionLocal()
    try:
        log = db.query(MedicationLog).filter(MedicationLog.id == log_id).first()
        if not log or log.confirmed or log.caregiver_notified:
            return

        elder = db.query(User).filter(User.telegram_id == elder_chat_id).first()
        if not elder: return
        elder_lang = elder.language if elder else "it"

        if not elder.caregiver_telegram_id:
            try:
                msg = await context.bot.send_message(
                    chat_id=elder_chat_id,
                    text=get_text("rem_elder_followup", elder_lang, medication_name),
                    parse_mode="Markdown",
                )
                context.user_data.setdefault('alert_msgs', {})[log_id] = msg.message_id
            except Exception: pass
            return

        cg_user = db.query(User).filter(User.telegram_id == elder.caregiver_telegram_id).first()
        cg_lang = cg_user.language if cg_user else "it"

        try:
            await context.bot.send_message(
                chat_id=elder.caregiver_telegram_id,
                text=get_text("rem_cg_alert", cg_lang, elder.first_name, CAREGIVER_TIMEOUT_MINUTES, medication_name, dosage),
                parse_mode="Markdown",
            )
            log.caregiver_notified = True
            db.commit()
        except Exception: pass

        try:
            msg = await context.bot.send_message(
                chat_id=elder_chat_id, 
                text=get_text("rem_elder_alert_sent", elder_lang),
                parse_mode="Markdown"
            )
            context.user_data.setdefault('alert_msgs', {})[log_id] = msg.message_id
        except Exception: pass

    finally:
        db.close()

async def rebuild_reminder_message(query, logs, lang, context):
    text = get_text("rem_multi_title", lang)
    keyboard = []
    pending_logs = []

    for log in logs:
        medication = log.medication
        if log.confirmed:
            text += get_text("rem_med_line_done", lang, medication.name, medication.dosage)
        else:
            text += get_text("rem_med_line", lang, medication.name, medication.dosage)
            pending_logs.append(log)
            keyboard.append([InlineKeyboardButton(f"✅ {medication.name}", callback_data=f"confirm_{log.id}")])

    if pending_logs:
        all_pending_ids = ",".join(str(log.id) for log in pending_logs)
        
        if len(pending_logs) > 1:
            keyboard.append([InlineKeyboardButton(get_text("btn_confirm_all", lang), callback_data=f"confirm_all_{all_pending_ids}")])
            
        keyboard.append([InlineKeyboardButton(get_text("btn_snooze", lang, REMINDER_SNOOZE_MINUTES), callback_data=f"snooze_all_{all_pending_ids}")])
    else:
        text += get_text("rem_all_confirmed", lang)
        keyboard.append([InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="mostra_help")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
    if not pending_logs:
        salva_id_tastiera(context, query.message.message_id)


# --- NUOVA SEZIONE: FLUSSI DI DOPPIA CONFERMA ---

async def confirm_medication(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fase 1: Chiede la doppia conferma per un singolo farmaco."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'it')

    log_id = int(query.data.split("_")[1])
    db = SessionLocal()
    try:
        log = db.query(MedicationLog).filter(MedicationLog.id == log_id).first()
        if not log:
            await query.edit_message_text(get_text("rem_not_found", lang))
            return
        if log.confirmed:
            await query.edit_message_text(get_text("rem_already_confirmed", lang))
            return

        text = get_text("rem_ask_sure", lang, log.medication.name)
        keyboard = [
            [InlineKeyboardButton(get_text("btn_yes_confirm", lang), callback_data=f"really_confirm_{log_id}")],
            [InlineKeyboardButton(get_text("btn_no_cancel", lang), callback_data=f"cancel_confirm_{log_id}")]
        ]
        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    finally:
        db.close()


async def cancel_confirm_medication(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fase 1-B: Se l'utente clicca 'No', ricostruisce il reminder intatto."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'it')
    
    log_id = int(query.data.replace("cancel_confirm_", ""))
    db = SessionLocal()
    try:
        log = db.query(MedicationLog).filter(MedicationLog.id == log_id).first()
        if not log: return
        
        start_window = log.scheduled_time - timedelta(seconds=5)
        end_window = log.scheduled_time + timedelta(seconds=5)
        same_time_logs = db.query(MedicationLog).join(Medication).filter(
            Medication.user_id == update.effective_user.id,
            MedicationLog.scheduled_time >= start_window,
            MedicationLog.scheduled_time <= end_window
        ).all()

        await rebuild_reminder_message(query, same_time_logs, lang, context)
    finally:
        db.close()


async def really_confirm_medication(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fase 2: Salvataggio effettivo nel DB (vecchia logica)."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'it')

    log_id = int(query.data.replace("really_confirm_", ""))
    
    alert_msg_id = context.user_data.get('alert_msgs', {}).pop(log_id, None)
    if alert_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=alert_msg_id)
        except Exception:
            pass

    db = SessionLocal()
    try:
        log = db.query(MedicationLog).filter(MedicationLog.id == log_id).first()
        if not log:
            await query.edit_message_text(get_text("rem_not_found", lang))
            return
        if log.confirmed:
            await query.edit_message_text(get_text("rem_already_confirmed", lang))
            return

        log.confirmed = True
        log.confirmed_at = datetime.now(ZoneInfo("Europe/Rome"))
        caregiver_was_notified = log.caregiver_notified
        db.commit()

        start_window = log.scheduled_time - timedelta(seconds=5)
        end_window = log.scheduled_time + timedelta(seconds=5)

        same_time_logs = db.query(MedicationLog).join(Medication).filter(
            Medication.user_id == update.effective_user.id,
            MedicationLog.scheduled_time >= start_window,
            MedicationLog.scheduled_time <= end_window
        ).all()

        await rebuild_reminder_message(query, same_time_logs, lang, context)

        if caregiver_was_notified:
            elder = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
            if elder and elder.caregiver_telegram_id:
                cg_user = db.query(User).filter(User.telegram_id == elder.caregiver_telegram_id).first()
                cg_lang = cg_user.language if cg_user else "it"
                try:
                    await context.bot.send_message(
                        chat_id=elder.caregiver_telegram_id,
                        text=get_text("rem_cg_followup_success", cg_lang, elder.first_name, log.medication.name, log.confirmed_at.strftime('%H:%M')),
                        parse_mode="Markdown",
                    )
                except Exception: pass
    finally:
        db.close()


async def confirm_all_medications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fase 1 (Multipla): Chiede la doppia conferma per tutti i farmaci."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "it")

    raw_ids = query.data.replace("confirm_all_", "")
    
    text = get_text("rem_ask_sure_all", lang)
    keyboard = [
        [InlineKeyboardButton(get_text("btn_yes_confirm", lang), callback_data=f"really_confirm_all_{raw_ids}")],
        [InlineKeyboardButton(get_text("btn_no_cancel", lang), callback_data=f"cancel_confirm_all_{raw_ids}")]
    ]
    await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def cancel_confirm_all_medications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fase 1-B (Multipla): Ritorna indietro se annulla il Conferma Tutti."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "it")

    raw_ids = query.data.replace("cancel_confirm_all_", "")
    log_ids = [int(x) for x in raw_ids.split(",")]
    db = SessionLocal()
    try:
        logs = db.query(MedicationLog).filter(MedicationLog.id.in_(log_ids)).all()
        if not logs: return
        
        # Uso il primo log per trovare la finestra temporale
        start_window = logs[0].scheduled_time - timedelta(seconds=5)
        end_window = logs[0].scheduled_time + timedelta(seconds=5)

        same_time_logs = db.query(MedicationLog).join(Medication).filter(
            Medication.user_id == update.effective_user.id,
            MedicationLog.scheduled_time >= start_window,
            MedicationLog.scheduled_time <= end_window
        ).all()

        await rebuild_reminder_message(query, same_time_logs, lang, context)
    finally:
        db.close()


async def really_confirm_all_medications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fase 2 (Multipla): Salvataggio effettivo nel DB (vecchia logica)."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "it")

    raw_ids = query.data.replace("really_confirm_all_", "")
    log_ids = [int(x) for x in raw_ids.split(",")]
    
    alert_msgs = context.user_data.get('alert_msgs', {})
    for lid in log_ids:
        alert_msg_id = alert_msgs.pop(lid, None)
        if alert_msg_id:
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=alert_msg_id)
            except Exception:
                pass

    db = SessionLocal()
    try:
        logs = db.query(MedicationLog).filter(MedicationLog.id.in_(log_ids)).all()
        if not logs:
            await query.answer(get_text("alert_no_meds", lang), show_alert=True)
            return

        confirmed_count = 0
        now = datetime.now(ZoneInfo("Europe/Rome"))

        for log in logs:
            if log.confirmed: continue
            log.confirmed = True
            log.confirmed_at = now
            confirmed_count += 1

        db.commit()

        if confirmed_count == 0:
            await query.answer(get_text("alert_already_confirmed", lang))
            return

        updated_logs = db.query(MedicationLog).filter(MedicationLog.id.in_(log_ids)).all()
        await rebuild_reminder_message(query, updated_logs, lang, context)

    finally:
        db.close()


# --- FINE DOPPIA CONFERMA ---


async def send_snoozed_reminder(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.data
    user_id = job_data["user_id"]
    log_ids = job_data["log_ids"]

    db = SessionLocal()
    try:
        logs = db.query(MedicationLog).filter(MedicationLog.id.in_(log_ids)).all()
        if not logs: return

        pending_logs = [log for log in logs if not log.confirmed]
        if not pending_logs: return

        elder = db.query(User).filter(User.telegram_id == user_id).first()
        elder_lang = elder.language if elder else "it"
        text = get_text("rem_snoozed_title", elder_lang)
        keyboard = []

        for log in pending_logs:
            medication = log.medication
            text += get_text("rem_med_line", elder_lang, medication.name, medication.dosage)
            keyboard.append([InlineKeyboardButton(f"✅ {medication.name}", callback_data=f"confirm_{log.id}")])

        pending_ids = ",".join(str(log.id) for log in pending_logs)
        
        if len(pending_logs) > 1:
            keyboard.append([InlineKeyboardButton(get_text("btn_confirm_all", elder_lang), callback_data=f"confirm_all_{pending_ids}")])
            
        keyboard.append([InlineKeyboardButton(get_text("btn_snooze", elder_lang, REMINDER_SNOOZE_MINUTES), callback_data=f"snooze_all_{pending_ids}")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await disinnesca_vecchia_tastiera(user_id, context)

        msg = await context.bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        salva_id_tastiera(context, msg.message_id)
    finally:
        db.close()

async def snooze_all_medications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "it")

    raw_ids = query.data.replace("snooze_all_", "")
    log_ids = [int(x) for x in raw_ids.split(",")]
    
    alert_msgs = context.user_data.get('alert_msgs', {})
    for lid in log_ids:
        alert_msg_id = alert_msgs.pop(lid, None)
        if alert_msg_id:
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=alert_msg_id)
            except Exception:
                pass
                
    db = SessionLocal()
    try:
        logs = db.query(MedicationLog).filter(MedicationLog.id.in_(log_ids)).all()
        if not logs:
            await query.answer(get_text("alert_reminder_not_found", lang), show_alert=True)
            return

        pending_logs = [log for log in logs if not log.confirmed]
        if not pending_logs:
            await query.answer(get_text("alert_all_confirmed", lang), show_alert=True)
            return

        user_id = update.effective_user.id

        for log in pending_logs:
            escalation_job_name = f"escalation_{log.id}"
            current_jobs = context.application.job_queue.get_jobs_by_name(escalation_job_name)
            for job in current_jobs:
                job.schedule_removal()

        context.application.job_queue.run_once(
            send_snoozed_reminder,
            when=REMINDER_SNOOZE_MINUTES * 60,
            data={"user_id": user_id, "log_ids": [log.id for log in pending_logs]},
            chat_id=user_id,
            user_id=user_id
        )

        for log in pending_logs:
            medication = log.medication
            context.application.job_queue.run_once(
                check_confirmation_and_notify_caregiver,
                when=(REMINDER_SNOOZE_MINUTES + CAREGIVER_TIMEOUT_MINUTES) * 60,
                data={
                    "log_id": log.id,
                    "elder_chat_id": user_id,
                    "medication_name": medication.name,
                    "dosage": medication.dosage,
                },
                name=f"escalation_{log.id}",
                chat_id=user_id,
                user_id=user_id
            )

        keyboard = [[InlineKeyboardButton(get_text("btn_main_menu", lang), callback_data="mostra_help")]]

        await query.edit_message_text(
            text=get_text("snooze_confirmed", lang, REMINDER_SNOOZE_MINUTES),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        salva_id_tastiera(context, query.message.message_id)

    finally:
        db.close()