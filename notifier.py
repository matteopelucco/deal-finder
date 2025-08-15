import asyncio
from telegram import Bot
from telegram.error import TelegramError
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

# Limite di caratteri di Telegram per le didascalie delle foto.
# Usiamo un valore leggermente inferiore per sicurezza.
CAPTION_LIMIT = 1020

async def invia_notifica(messaggio: str, link_annuncio: str, img_url: str = None):
    """
    Invia un messaggio di notifica, troncando la didascalia in modo intelligente
    per preservare sempre il link dell'annuncio.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("ERRORE: Token o Chat ID di Telegram non impostati.")
        return

    bot = Bot(token=TELEGRAM_TOKEN)
    
    # Costruiamo la parte finale del messaggio, che DEVE essere preservata.
    link_markdown = f"\n\n➡️ [Vedi Annuncio]({link_annuncio})"
    
    try:
        if img_url:
            # --- LOGICA DI TRONCAMENTO INTELLIGENTE ---
            
            # Calcoliamo lo spazio disponibile per il messaggio, sottraendo la lunghezza del link
            spazio_disponibile = CAPTION_LIMIT - len(link_markdown)
            
            # Se il messaggio principale è troppo lungo, lo tronchiamo
            if len(messaggio) > spazio_disponibile:
                messaggio_troncato = messaggio[:spazio_disponibile - 4] + "..." # Aggiungiamo '...'
            else:
                messaggio_troncato = messaggio
            
            # Componiamo la didascalia finale
            caption_finale = messaggio_troncato + link_markdown

            # Inviamo la foto con la didascalia sicura
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=img_url,
                caption=caption_finale,
                parse_mode='Markdown'
            )

        else: # Se non c'è immagine, il limite è 4096, quindi il rischio è basso
            messaggio_completo = messaggio + link_markdown
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=messaggio_completo,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
        print(f"Notifica inviata per: {link_annuncio}")

    except TelegramError as e:
        # Se anche dopo il troncamento il messaggio è troppo lungo, potrebbe esserci un altro errore.
        print(f"Errore durante l'invio della notifica Telegram: {e}")
        # --- STRATEGIA DI FALLBACK ---
        # Se l'invio della foto fallisce (magari per caption troppo lunga nonostante i calcoli),
        # proviamo a inviare un messaggio di testo semplice.
        print("Tentativo di invio come messaggio di testo di fallback...")
        try:
            messaggio_completo = messaggio + link_markdown
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"IMMAGINE: {img_url}\n\n{messaggio_completo}",
                parse_mode='Markdown'
            )
            print("Notifica di fallback inviata con successo.")
        except Exception as fallback_e:
            print(f"Anche l'invio di fallback è fallito: {fallback_e}")

    except Exception as e:
        print(f"Errore imprevisto nel notifier: {e}")