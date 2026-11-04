# app/utils/locales.py

TEXTS = {
    "it": {
        # --- MENU & NAVIGAZIONE ---
        "menu_title": "🤖 *Menu Assistente Salute*\n\nEcco cosa posso fare per te:\n\n📋 *Lista Farmaci*: Salva e gestisci i promemoria delle tue medicine.\n\n📖 *Bugiardino IA*: Leggi o fai domande sui foglietti illustrativi.\n\n👨‍⚕️ *Gestisci Caregiver*: Collega un familiare per farti aiutare.\n",
        "btn_main_menu": "❓ Menu principale",
        "btn_back_menu": "❓ Torna al Menu",
        "btn_cancel": "❌ Annulla",
        "btn_back": "🔙 Annulla",
        "msg_cancelled": "Operazione annullata.",
        "btn_language": "🌍 Cambia Lingua",
        "start_welcome": "Ciao {}! 👋 Sono l'Elder Health Assistant.\n\nSono qui per aiutarti a ricordare le tue medicine. Clicca sul bottone qui sotto per iniziare!",
        "btn_caregiver": "👨‍⚕️ Gestisci Caregiver",
        
        # --- SOTTOMENU LINGUA ---
        "lang_menu_title": "🌍 *Scegli la lingua / Choose language*\n\nSeleziona la lingua che preferisci adottare per il bot",
        
        # --- LISTA E AGGIUNTA ---
        "btn_list": "📋 La mia Lista",
        "btn_dosage": "Dose",
        "btn_time": "Orario",
        "btn_add_first": "➕ Aggiungi il primo Farmaco",
        "btn_add_another": "➕ Aggiungi nuovo Farmaco",
        "empty_list": "La tua lista è vuota.",
        "list_title": "💊 *Ecco la tua routine medica:*\n\n",
        "add_name": "💊 *Nuovo Farmaco*\n\nCome si chiama il medicinale? (es. Aspirina)",
        "add_dose": "Ottimo. Quanto ne devi prendere di *{}*?",
        "add_time": "Perfetto. A che ora devi prenderlo? \nN.B. Rispetta il formato HH:MM \n(es. 08:30, 11:00)",
        "add_success": "✅ *Salvato!*\n{} ({}) alle {}.",
        "invalid_dosage": "❌ Non ho capito la dose.\n\nScrivi una quantità che contenga un numero. Esempi:\n• `2`\n• `2 pillole`\n• `500mg`\n• `10 ml`\n\nRiprova:",
        
        # --- MODIFICA E ELIMINA ---
        "btn_edit_delete": "✏️ Modifica o Elimina",
        "btn_back_list": "📋 Torna alla lista",
        "mod_no_meds": "Non hai farmaci salvati da modificare.",
        "mod_select": "Quale farmaco vuoi modificare o eliminare?",
        "mod_not_found": "Farmaco non trovato.",
        "mod_what_to_edit": "👇 *Cosa vuoi modificare?*",
        "btn_mod_name": "✏️ Modifica NOME",
        "btn_mod_dose": "✏️ Modifica DOSE",
        "btn_mod_time": "✏️ Modifica ORARIO",
        "btn_delete": "❌ Elimina Farmaco",
        "delete_success": "✅ Il farmaco *{}* è stato eliminato.",
        "ask_new_name": "✍️ Scrivi il **NUOVO NOME** del farmaco:",
        "ask_new_dose": "✍️ Scrivi la **NUOVA DOSE** del farmaco:",
        "ask_new_time": "✍️ Scrivi il **NUOVO ORARIO** (formato HH:MM, es. 08:00):",
        "mod_success": "✅ Dati di *{}* aggiornati con successo!",
        
        # --- CAREGIVER ---
        "cg_menu_title_neutral": "👨‍⚕️ *Gestione Curatore*\n\nVuoi essere un curatore di un'altra persona, oppure vuoi che qualcuno ti faccia da curatore?",
        "btn_sono_curatore": "🤝 Sono il curatore",
        "btn_voglio_curatore": "🙋 Voglio un curatore",
        "cg_connect_setup": "👨‍⚕️ *Collega un curatore*\n\nDi' al tuo curatore di inserire questo codice:\n\n`{}`\n\nQuando l'avrà inserito, riceverai una notifica.",        "btn_rimuovi_curatore": "🚫 Rimuovi curatore",
        "cg_ask_code": "🔑 Inserisci il codice della persona che vuoi assistere:",
        "cg_role_taken_elder": "ℹ️ Hai già un curatore. Non puoi essere curatore di altri.",
        "cg_role_taken_caregiver": "ℹ️ Sei già curatore di *{}*. Non puoi avere a tua volta un curatore.",
        "cg_caregiver_status": "👨‍⚕️ *Sei il curatore di {}*\n\nPuoi gestire i suoi farmaci e ricevi notifiche se non conferma un'assunzione.",
        "cg_elder_status": "👨‍⚕️ *Hai un curatore: {}*\n\nSe non confermi un farmaco in tempo, sarà avvisato.",
        "cg_invalid_token": "❌ Codice non valido.\n\nControlla di aver scritto bene il codice. Se il problema continua, chiedi alla persona di generarne uno nuovo.",
        "cg_self_pairing": "❌ Non puoi essere il curatore di te stesso 🙂",
        "cg_caregiver_success": "✅ *Collegamento riuscito!*\n\nSei stato registrato come curatore di *{}*.\n\nRiceverai una notifica se non confermerà l'assunzione di un farmaco entro il tempo previsto.",
        "cg_elder_notification": "✅ *Curatore collegato!*\n\n*{}* ti farà da curatore. Sarà avvisato se non confermerai un farmaco in tempo.",
        "cg_no_cg_to_remove": "Nessun curatore da rimuovere.",

        # --- RIMOZIONE CON CONFERMA ---
        "cg_removal_requested_elder": "📨 Richiesta di rimozione inviata a *{}*.\n\nIl tuo curatore deve confermare prima che il legame venga eliminato. Riceverai un messaggio quando avrà risposto.",
        "cg_removal_request_to_cg": "⚠️ *{}* vuole rimuoverti come suo curatore.\n\nVuoi confermare?",
        "btn_conferma_rimozione": "✅ Conferma rimozione",
        "btn_annulla_rimozione": "❌ Annulla",
        "cg_removal_confirmed_cg": "✅ Hai confermato la rimozione. Non sei più curatore di *{}*.",
        "cg_removal_confirmed_elder": "✅ Il tuo curatore *{}* ha confermato la rimozione. Il legame è stato sciolto.",
        "cg_removal_cancelled_cg": "Ok, la richiesta è stata annullata. Resti curatore di *{}*.",
        "cg_removal_cancelled_elder": "ℹ️ *{}* ha rifiutato la richiesta di rimozione. Restate collegati.",
        "cg_no_pending_removal": "Nessuna richiesta in corso.",

        # --- CAREGIVER GESTISCE FARMACI ASSISTITO ---
        "add_for_whom": "👥 *Per chi vuoi aggiungere il farmaco?*",
        "btn_per_me": "👤 Per me",
        "btn_per_assistito": "👴 Per {}",
        "add_success_for_elder": "✅ *Salvato per {}!*\n{} ({}) alle {}.",
        "btn_lista_assistito": "📋 La lista di {}",
        "list_title_assistito": "💊 *Farmaci di {}:*\n\n",
        "empty_list_assistito": "{} non ha ancora farmaci salvati.",

        # --- PROMEMORIA E NOTIFICHE ---
        "rem_elder_followup": "⏰ Non hai ancora confermato il farmaco *{}*.\n\nRicordati di prenderlo!",
        "rem_cg_alert": "⚠️ *Avviso caregiver*\n\n*{:s}* non ha confermato l'assunzione del farmaco entro {} minuti.\n\n💊 Farmaco: *{}*\n📦 Dosaggio: {}\n\nTi consigliamo di contattare la persona per verificare.",
        "rem_elder_alert_sent": "⏰ Non hai confermato l'assunzione in tempo.\n\nHo avvisato il tuo caregiver. Ricordati di prendere il farmaco!",
        "rem_not_found": "❌ Reminder non trovato.",
        "rem_already_confirmed": "✅ Assunzione già confermata.",
        "rem_cg_followup_success": "✅ *Aggiornamento*\n\n*{}* ha appena confermato l'assunzione di *{}* alle {}.\n\nVa tutto bene 👍",
        "snooze_confirmed": "⏰ *Reminder rimandato*\n\nTi ricorderò di nuovo i farmaci tra 15 minuti.",
        "rem_multi_title": "💊 *Promemoria Farmaci*\n\nConferma i farmaci che hai assunto tra quelli che hai salvato:\n\n",
        "rem_med_line": "• *{}*\n  📦 {}\n\n",
        "rem_med_line_done": "✅ *{}*\n  📦 {}\n\n",
        "btn_confirm_all": "✅ Conferma tutti",
        "btn_snooze": "⏰ Rimanda 15 minuti",
        "rem_all_confirmed": "🎉 *Tutti i farmaci sono stati confermati.*",
        "rem_snoozed_title": "⏰ *Promemoria Rimandato*\n\n",
        "alert_no_meds": "Nessun farmaco trovato",
        "alert_already_confirmed": "Farmaci già confermati",
        "alert_reminder_not_found": "Reminder non trovato",
        "alert_all_confirmed": "Tutti i farmaci sono già confermati",
        "rem_ask_sure": "⚠️ *Conferma Assunzione*\n\nSei sicuro di aver già assunto *{}*?\nNon confermare se non l'hai ancora fatto.",
        "rem_ask_sure_all": "⚠️ *Conferma Assunzione*\n\nSei sicuro di aver già assunto **TUTTE** le medicine previste?\nNon confermare se non l'hai ancora fatto.",
        "btn_yes_confirm": "✅ Sì, confermo",
        "btn_no_cancel": "❌ No, torna indietro",

        # --- BUGIARDINO IA ---
        "btn_leaflet": "📖 Leggi Bugiardino",
        "leaf_welcome": "📖 *Bugiardino Intelligente*\n\nDi quale farmaco vuoi leggere le informazioni?\nScrivi il nome qui sotto (es. Aspirina, Tachipirina):",
        "leaf_loading": "⏳ Sto cercando e leggendo il bugiardino di {}...",
        "leaf_checking": "⏳ Controllo il bugiardino...",
        "leaf_thinking": "⏳ Ci penso...",
        "leaf_disclaimer": "⚠️ ATTENZIONE: Sono un'IA. Queste informazioni non sostituiscono il parere del medico.\n\n",
        "leaf_options": "(Scegli un'opzione qui sotto o scrivimi una domanda:)",
        "btn_leaf_summary": "📝 Riassunto Intelligente",
        "btn_leaf_doses": "⚖️ Dosi Consigliate",
        "btn_leaf_close": "❌ Chiudi Bugiardino",
        "leaf_closed": "Bugiardino chiuso.",
        "btn_read_another_leaflet": "📖 Leggi un altro Bugiardino",
        "leaf_error": "❌ Si è verificato un errore di connessione. Riprova più tardi."
        
    },
    
    "en": {
        # --- MENU & NAVIGATION ---
        "menu_title": "🤖 *Health Assistant Menu*\n\nHere is what I can do for you:\n\n📋 *Meds List*: Save and manage reminders for your medications.\n\n📖 *Smart Leaflet*: Read or ask questions about medication leaflets.\n\n👨‍⚕️ *Manage Caregiver*: Connect a family member to help you.\n",
        "btn_main_menu": "❓ Main Menu",
        "btn_back_menu": "❓ Back to Menu",
        "btn_cancel": "❌ Cancel",
        "btn_back": "🔙 Cancel",
        "msg_cancelled": "Operation cancelled.",
        "btn_language": "🌍 Change Language",
        "start_welcome": "Hello {}! 👋 I am the Elder Health Assistant.\n\nI'm here to help you remember your medications. Click the button below to start!",
        "btn_caregiver": "👨‍⚕️ Manage Caregiver",
        
        # --- LANGUAGE SUBMENU ---
        "lang_menu_title": "🌍 *Scegli la lingua / Choose language*\n\nSelect your preferred language for the bot",
        
        # --- LIST AND ADD ---
        "btn_list": "📋 My Meds List",
        "btn_dosage": "Dosage",
        "btn_time": "Time",
        "btn_add_first": "➕ Add your first Medication",
        "btn_add_another": "➕ Add new Medication",
        "empty_list": "Your list is empty.",
        "list_title": "💊 *Here is your medical routine:*\n\n",
        "add_name": "💊 *New Medication*\n\nWhat is the name of the medicine? (e.g., Aspirin)",
        "add_dose": "Great. How much *{}* do you need to take?",
        "add_time": "Perfect. At what time? \nNote: Use HH:MM format \n(e.g., 08:30, 11:00)",
        "add_success": "✅ *Saved!*\n{} ({}) at {}.",
        "invalid_dosage": "❌ I didn't understand the dose.\n\nType a quantity that contains a number. Examples:\n• `2`\n• `2 pills`\n• `500mg`\n• `10 ml`\n\nTry again:",
        
        # --- EDIT AND DELETE ---
        "btn_edit_delete": "✏️ Edit or Delete",
        "btn_back_list": "📋 Back to list",
        "mod_no_meds": "You have no saved medications to edit.",
        "mod_select": "Which medication do you want to edit or delete?",
        "mod_not_found": "Medication not found.",
        "mod_what_to_edit": "👇 *What do you want to edit?*",
        "btn_mod_name": "✏️ Edit NAME",
        "btn_mod_dose": "✏️ Edit DOSE",
        "btn_mod_time": "✏️ Edit TIME",
        "btn_delete": "❌ Delete Medication",
        "delete_success": "✅ The medication *{}* has been deleted.",
        "ask_new_name": "✍️ Type the **NEW NAME** of the medication:",
        "ask_new_dose": "✍️ Type the **NEW DOSE** of the medication:",
        "ask_new_time": "✍️ Type the **NEW TIME** (HH:MM format, e.g., 08:00):",
        "mod_success": "✅ Data for *{}* updated successfully!",
        
        # --- CAREGIVER ---
        "cg_menu_title_neutral": "👨‍⚕️ *Caregiver Management*\n\nDo you want to be a caregiver for someone else, or do you want to have a caregiver?",
        "btn_sono_curatore": "🤝 I am a caregiver",
        "btn_voglio_curatore": "🙋 I want a caregiver",
        "cg_connect_setup": "👨‍⚕️ *Connect a caregiver*\n\nTell your caregiver to enter this code:\n\n`{}`\n\nOnce they enter it, you'll receive a notification.",        "cg_ask_code": "🔑 Enter the code of the person you want to assist:",
        "cg_role_taken_elder": "ℹ️ You already have a caregiver. You cannot also be a caregiver to others.",
        "cg_role_taken_caregiver": "ℹ️ You are already a caregiver for *{}*. You cannot also have a caregiver yourself.",
        "cg_caregiver_status": "👨‍⚕️ *You are the caregiver of {}*\n\nYou can manage their medications and you'll be notified if they don't confirm a dose.",
        "cg_elder_status": "👨‍⚕️ *Your caregiver is: {}*\n\nIf you don't confirm a medication on time, they will be notified.",
        "cg_invalid_token": "❌ Invalid code.\n\nPlease check if you typed the code correctly. If the issue persists, ask the person to generate a new one.",
        "cg_self_pairing": "❌ You cannot be your own caregiver 🙂",
        "cg_caregiver_success": "✅ *Connection successful!*\n\nYou have been registered as the caregiver for *{}*.\n\nYou will receive a notification if they do not confirm a medication within the expected time.",
        "cg_elder_notification": "✅ *Caregiver connected!*\n\n*{}* will be your caregiver. They will be notified if you don't confirm a medication on time.",
        "cg_no_cg_to_remove": "No caregiver to remove.",

        # --- REMOVAL WITH CONFIRMATION ---
        "cg_removal_requested_elder": "📨 Removal request sent to *{}*.\n\nYour caregiver must confirm before the link is removed. You will receive a message when they respond.",
        "cg_removal_request_to_cg": "⚠️ *{}* wants to remove you as their caregiver.\n\nDo you want to confirm?",
        "btn_conferma_rimozione": "✅ Confirm removal",
        "btn_annulla_rimozione": "❌ Cancel",
        "cg_removal_confirmed_cg": "✅ You have confirmed the removal. You are no longer the caregiver of *{}*.",
        "cg_removal_confirmed_elder": "✅ Your caregiver *{}* has confirmed the removal. The link has been dissolved.",
        "cg_removal_cancelled_cg": "Ok, the request has been cancelled. You remain the caregiver of *{}*.",
        "cg_removal_cancelled_elder": "ℹ️ *{}* declined the removal request. You stay connected.",
        "cg_no_pending_removal": "No pending request.",

        # --- CAREGIVER MANAGES ELDER'S MEDS ---
        "add_for_whom": "👥 *Who is this medication for?*",
        "btn_per_me": "👤 For me",
        "btn_per_assistito": "👴 For {}",
        "add_success_for_elder": "✅ *Saved for {}!*\n{} ({}) at {}.",
        "btn_lista_assistito": "📋 {}'s list",
        "list_title_assistito": "💊 *{}'s medications:*\n\n",
        "empty_list_assistito": "{} has no saved medications yet.",

        # --- REMINDERS & NOTIFICATIONS ---
        "rem_elder_followup": "⏰ You haven't confirmed taking *{}* yet.\n\nRemember to take it!",
        "rem_cg_alert": "⚠️ *Caregiver Alert*\n\n*{:s}* did not confirm taking their medication within {} minutes.\n\n💊 Medication: *{}*\n📦 Dosage: {}\n\nWe recommend contacting them to check.",
        "rem_elder_alert_sent": "⏰ You did not confirm your medication on time.\n\nI have notified your caregiver. Remember to take your medicine!",
        "rem_not_found": "❌ Reminder not found.",
        "rem_already_confirmed": "✅ Intake already confirmed.",
        "rem_cg_followup_success": "✅ *Update*\n\n*{}* just confirmed taking *{}* at {}.\n\nEverything is fine 👍",
        "rem_multi_title": "💊 *Medication Reminder*\n\nConfirm the medications you have taken from the list below:\n\n",
        "rem_med_line": "• *{}*\n  📦 {}\n\n",
        "rem_med_line_done": "✅ *{}*\n  📦 {}\n\n",
        "btn_confirm_all": "✅ Confirm all",
        "btn_snooze": "⏰ Snooze 15 minutes",
        "rem_all_confirmed": "🎉 *All medications have been confirmed.*",
        "rem_snoozed_title": "⏰ *Snoozed Reminder*\n\n",
        "snooze_confirmed": "⏰ *Reminder snoozed*\n\nI'll remind you about your medications again in 15 minutes.",
        "alert_no_meds": "No medication found",
        "alert_already_confirmed": "Medications already confirmed",
        "alert_reminder_not_found": "Reminder not found",
        "alert_all_confirmed": "All medications are already confirmed",
        "rem_ask_sure": "⚠️ *Confirm Intake*\n\nAre you sure you have already taken *{}*?\nDo not confirm if you haven't yet.",
        "rem_ask_sure_all": "⚠️ *Confirm Intake*\n\nAre you sure you have already taken **ALL** the scheduled medications?\nDo not confirm if you haven't yet.",
        "btn_yes_confirm": "✅ Yes, I confirm",
        "btn_no_cancel": "❌ No, go back",

        # --- AI LEAFLET ---
        "btn_leaflet": "📖 Read Leaflet",
        "leaf_welcome": "📖 *Smart Leaflet*\n\nWhich medication do you want to read about?\nType the name below (e.g., Aspirin, Tylenol):",
        "leaf_loading": "⏳ Searching and reading the leaflet for {}...",
        "leaf_checking": "⏳ Checking the leaflet...",
        "leaf_thinking": "⏳ Thinking...",
        "leaf_disclaimer": "⚠️ WARNING: I am an AI. This information does not replace professional medical advice.\n\n",
        "leaf_options": "(Choose an option below or type a question:)",
        "btn_leaf_summary": "📝 Smart Summary",
        "btn_leaf_doses": "⚖️ Recommended Doses",
        "btn_leaf_close": "❌ Close Leaflet",
        "leaf_closed": "Leaflet closed.",
        "btn_read_another_leaflet": "📖 Read another Leaflet",
        "leaf_error": "❌ A connection error occurred. Please try again later."
    }
}

def get_text(key: str, lang: str = "it", *args) -> str:
    if lang not in TEXTS:
        lang = "it"
    text = TEXTS[lang].get(key, f"[MISSING TRANSLATION: {key}]")
    if args:
        return text.format(*args)
    return text