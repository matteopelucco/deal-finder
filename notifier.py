from telegram import Bot
from telegram.error import TelegramError
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

# Definiamo il limite di sicurezza per le didascalie. Telegram è 1024.
# Usiamo 1000 per avere un po' di margine.
CAPTION_LIMIT = 1000

async def invia_notifica(messaggio: str, link_annuncio: str, img_url: str = None):
    """Invia un messaggio di notifica, troncando la didascalia se troppo lunga."""
    bot = Bot(token=TELEGRAM_TOKEN)
    
    # Uniamo subito il messaggio e il link per avere la versione completa
    testo_completo = f"{messaggio}\n\n➡️ [Vedi Annuncio]({link_annuncio})"
    
    try:
        if img_url:
            caption_da_inviare = testo_completo
            # --> CONTROLLO E TRONCAMENTO
            if len(caption_da_inviare) > CAPTION_LIMIT:
                # Taglia il messaggio e aggiungi un indicatore
                caption_da_inviare = caption_da_inviare[:CAPTION_LIMIT] + "... (messaggio troncato)"
            
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=img_url,
                caption=caption_da_inviare, # -> Usa la versione potenzialmente troncata
                parse_mode='Markdown'
            )
        else:
            # Per i messaggi di solo testo, il limite è più alto (4096), quindi meno rischioso.
            # Non applichiamo il troncamento qui per semplicità.
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=testo_completo,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
        print(f"Notifica inviata per: {link_annuncio}")
    except TelegramError as e:
        print(f"Errore durante l'invio della notifica Telegram: {e}")