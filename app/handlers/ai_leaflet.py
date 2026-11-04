# app/handlers/ai_leaflet.py
import os
from google import genai
from google.genai import types
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from app.utils.locales import get_text
from app.utils.ui import disinnesca_vecchia_tastiera, salva_id_tastiera

NOME_FARMACO, DOMANDE = range(2)

SYSTEM_PROMPT_IT = (
    "Sei un assistente farmaceutico esperto, preciso e cauto. "
    "Non sei un medico. Non puoi prescrivere farmaci o dare consigli medici personali. "
    "Devi rispondere esclusivamente basandoti sulle informazioni ufficiali dei foglietti illustrativi (bugiardini). "
    "Se ti viene chiesto qualcosa che non sai con assoluta certezza, devi rispondere: "
    "'Non ho questa informazione, per favore consulta il tuo medico.' "
    "Il tuo utente è un anziano che cerca informazioni chiare e semplici sui farmaci. "
    "IMPORTANTE: NON usare alcun tipo di formattazione speciale relativa a Markdown, come asterischi o underscore nella risposta."
)

SYSTEM_PROMPT_EN = (
    "You are an expert, precise, and cautious pharmaceutical assistant. "
    "You are not a doctor. You cannot prescribe medications or give personal medical advice. "
    "You must answer exclusively based on the official patient information leaflets. "
    "If you are asked something you do not know with absolute certainty, you must answer: "
    "'I do not have this information, please consult your doctor.' "
    "Your user is an elderly person looking for clear and simple information about medications. "
    "IMPORTANT: DO NOT use any special Markdown formatting, such as asterisks or underscores in the response."
)

def get_system_prompt(lang: str) -> str:
    return SYSTEM_PROMPT_EN if lang == "en" else SYSTEM_PROMPT_IT

def get_bugiardino_keyboard(lang: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text("btn_leaf_summary", lang), callback_data="riassunto_farmaco")],
        [InlineKeyboardButton(get_text("btn_leaf_doses", lang), callback_data="dosi_farmaco")],
        [InlineKeyboardButton(get_text("btn_leaf_close", lang), callback_data="annulla_bugiardino")]
    ])

def get_error_keyboard(lang: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text("btn_read_another_leaflet", lang), callback_data="inizia_bugiardino")],
        [InlineKeyboardButton(get_text("btn_back_menu", lang), callback_data="mostra_help")]
    ])

async def inizia_bugiardino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    lang = context.user_data.get('lang', 'it')

    # Siamo nel flusso di navigazione, generiamo nuovo messaggio e disinneschiamo il vecchio
    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)

    keyboard = [[InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="annulla_bugiardino")]]
    
    msg = await update.effective_message.reply_text(
        get_text("leaf_welcome", lang), 
        parse_mode="Markdown", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    salva_id_tastiera(context, msg.message_id)
    context.user_data['leaf_prompt_msg_id'] = msg.message_id
    
    return NOME_FARMACO

async def analizza_farmaco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nome_farmaco = update.message.text
    context.user_data['farmaco_corrente'] = nome_farmaco
    lang = context.user_data.get('lang', 'it')
    
    # 1. Rimuoviamo la tastiera dal messaggio iniziale per la logica interna del bugiardino
    prompt_msg_id = context.user_data.get('leaf_prompt_msg_id')
    if prompt_msg_id:
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=update.effective_chat.id,
                message_id=prompt_msg_id,
                reply_markup=None
            )
        except Exception:
            pass 
    
    # 2. Questo è un nuovo messaggio generato dal bot
    keyboard_attesa = [[InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="annulla_bugiardino")]]
    msg = await update.message.reply_text(
        get_text("leaf_loading", lang, nome_farmaco),
        reply_markup=InlineKeyboardMarkup(keyboard_attesa)
    )
    salva_id_tastiera(context, msg.message_id)
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    try:
        if lang == "en":
            prompt = f"Provide a clear, simple summary in English suitable for an elderly person of the package leaflet for the drug: {nome_farmaco}. Include: What it is used for, How to use it, and Main Side Effects."
        else:
            prompt = f"Fornisci un riassunto chiaro, in italiano e comprensibile per un anziano del bugiardino del farmaco: {nome_farmaco}. Includi: A cosa serve, Come si usa, e Principali Effetti Collaterali."
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=get_system_prompt(lang))
        )
        
        disclaimer = get_text("leaf_disclaimer", lang)
        farmaco_label = "Drug" if lang == "en" else "Farmaco"
        
        # 3. Aggiorniamo questo messaggio. Essendo un edit, la tastiera attiva rimane registrata correttamente
        await msg.edit_text(
            text=f"{disclaimer}{farmaco_label}: {nome_farmaco.upper()}\n\n{response.text}\n\n{get_text('leaf_options', lang)}",
            reply_markup=get_bugiardino_keyboard(lang)
        )
        return DOMANDE
    except Exception as e:
        await msg.edit_text(get_text("leaf_error", lang), reply_markup=get_error_keyboard(lang))
        return ConversationHandler.END

async def azione_rapida_bugiardino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'it')
    
    azione = query.data
    farmaco = context.user_data.get('farmaco_corrente', 'this drug')
    
    # Anche questo genera un nuovo messaggio a scendere, così l'anziano non perde il bugiardino di prima
    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)
    keyboard_attesa = [[InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="annulla_bugiardino")]]
    msg = await update.effective_message.reply_text(
        get_text("leaf_checking", lang),
        reply_markup=InlineKeyboardMarkup(keyboard_attesa)
    )
    salva_id_tastiera(context, msg.message_id)
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    if azione == "riassunto_farmaco":
        prompt = f"Make an extremely concise, smart, and bullet-point summary of the leaflet for the drug {farmaco}." if lang == "en" else f"Fai un riassunto estremamente sintetico, intelligente e per punti chiave del bugiardino del farmaco {farmaco}."
    elif azione == "dosi_farmaco":
        prompt = f"Clearly and simply list ONLY the recommended dosages and posology reported in the leaflet for the drug {farmaco}." if lang == "en" else f"Elenca in modo chiaro e semplice ESCLUSIVAMENTE le dosi consigliate e la posologia riportate nel bugiardino del farmaco {farmaco}."
    else:
        return DOMANDE
        
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=get_system_prompt(lang))
        )
        await msg.edit_text(text=response.text, reply_markup=get_bugiardino_keyboard(lang))
        return DOMANDE
    except Exception as e:
        await msg.edit_text(get_text("leaf_error", lang), reply_markup=get_error_keyboard(lang))
        return ConversationHandler.END

async def rispondi_domanda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    domanda = update.message.text
    farmaco = context.user_data.get('farmaco_corrente', 'this drug')
    lang = context.user_data.get('lang', 'it')
    
    await disinnesca_vecchia_tastiera(update.effective_chat.id, context)
    keyboard_attesa = [[InlineKeyboardButton(get_text("btn_cancel", lang), callback_data="annulla_bugiardino")]]
    msg = await update.message.reply_text(
        get_text("leaf_thinking", lang),
        reply_markup=InlineKeyboardMarkup(keyboard_attesa)
    )
    salva_id_tastiera(context, msg.message_id)
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    try:
        prompt = f"Regarding the drug {farmaco}, the user asks: '{domanda}'. Answer in a simple way based on the leaflet." if lang == "en" else f"Riguardo al farmaco {farmaco}, l'utente chiede: '{domanda}'. Rispondi in modo semplice basandoti sul bugiardino."
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=get_system_prompt(lang))
        )
        await msg.edit_text(text=response.text, reply_markup=get_bugiardino_keyboard(lang))
        return DOMANDE
    except Exception as e:
        await msg.edit_text(get_text("leaf_error", lang), reply_markup=get_error_keyboard(lang))
        return ConversationHandler.END

async def annulla_bugiardino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    lang = context.user_data.get('lang', 'it')
    
    if 'farmaco_corrente' in context.user_data:
        del context.user_data['farmaco_corrente']
        
    keyboard = [
        [InlineKeyboardButton(get_text("btn_read_another_leaflet", lang), callback_data="inizia_bugiardino")],
        [InlineKeyboardButton(get_text("btn_back_menu", lang), callback_data="mostra_help")]
    ]
    
    if query:
        await query.edit_message_text(get_text("leaf_closed", lang), reply_markup=InlineKeyboardMarkup(keyboard))
        salva_id_tastiera(context, query.message.message_id)
    else:
        await disinnesca_vecchia_tastiera(update.effective_chat.id, context)
        msg = await update.effective_message.reply_text(get_text("leaf_closed", lang), reply_markup=InlineKeyboardMarkup(keyboard))
        salva_id_tastiera(context, msg.message_id)
        
    return ConversationHandler.END

bugiardino_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(inizia_bugiardino, pattern="^inizia_bugiardino$")],
    states={
        NOME_FARMACO: [MessageHandler(filters.TEXT & ~filters.COMMAND, analizza_farmaco)],
        DOMANDE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, rispondi_domanda),
            CallbackQueryHandler(azione_rapida_bugiardino, pattern="^(riassunto_farmaco|dosi_farmaco)$")
        ]
    },
    fallbacks=[CallbackQueryHandler(annulla_bugiardino, pattern="^annulla_bugiardino$")]
)