from telegram import Bot
from telegram.error import TelegramError
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
def invia_notifica(messaggio: str, link_annuncio: str, img_url: str = None):
    """Invia un messaggio di notifica formattato a un canale Telegram."""
    bot = Bot(token=TELEGRAM_TOKEN)
    testo_completo = f"{messaggio}\n\n➡️ [Vedi Annuncio]({link_annuncio})"
    
    try:
        if img_url:
            bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=img_url,
                caption=testo_completo,
                parse_mode='Markdown'
            )
        else:
            bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=testo_completo,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
        print(f"Notifica inviata per: {link_annuncio}")
    except TelegramError as e:
        print(f"Errore durante l'invio della notifica Telegram: {e}")