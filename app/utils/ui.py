# app/utils/ui.py
from telegram.ext import ContextTypes

async def disinnesca_vecchia_tastiera(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """
    Cerca l'ID dell'ultimo messaggio con bottoni inviato e, se esiste, 
    rimuove la tastiera lasciando intatto il testo.
    """
    old_msg_id = context.user_data.get('ultimo_messaggio_con_bottoni_id')
    
    if old_msg_id:
        try:
            # Modifichiamo il vecchio messaggio impostando i bottoni a None (vuoto)
            await context.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=old_msg_id,
                reply_markup=None
            )
        except Exception:
            # Ignoriamo l'errore se l'utente ha cancellato il messaggio a mano
            # o se il messaggio è troppo vecchio per essere modificato
            pass
        finally:
            # Puliamo la memoria per evitare disinneschi doppi
            context.user_data['ultimo_messaggio_con_bottoni_id'] = None

def salva_id_tastiera(context: ContextTypes.DEFAULT_TYPE, message_id: int):
    """Salva in memoria l'ID del nuovo messaggio con i bottoni."""
    context.user_data['ultimo_messaggio_con_bottoni_id'] = message_id