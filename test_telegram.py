import sys
import asyncio  # -> Importa la libreria asyncio
from telegram import Bot
from telegram.error import TelegramError

# --- INSERISCI QUI LE TUE CREDENZIALI ---
# Copia e incolla gli stessi valori che hai inserito in config.py
TELEGRAM_TOKEN = "8237781386:AAHUPoO31Up55iO-dHABpN-VM9VeNAh0GHE"
TELEGRAM_CHAT_ID = "11077371"
# -----------------------------------------

async def test_telegram_message():  # -> Rendi la funzione "async"
    """
    Invia un semplice messaggio di testo a Telegram per verificare la configurazione.
    """
    if "INSERISCI" in TELEGRAM_TOKEN or "INSERISCI" in TELEGRAM_CHAT_ID:
        print("🛑 ERRORE: Inserisci TOKEN e CHAT_ID reali nel file.")
        sys.exit(1)
    print("Inizio test di connessione asincrono con Telegram...")
    
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        messaggio_di_testo = (
            "✅ **Test Asincrono Riuscito!** ✅\n\n"
            "Ciao! Sono il tuo bot *Deal Finder*.\n"
            "La libreria `python-telegram-bot` è asincrona e ora comunichiamo correttamente."
        )
        
        # -> Aggiungi "await" prima della chiamata al bot
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=messaggio_di_testo,
            parse_mode='Markdown'
        )
        
        print("\n🎉 Successo! Messaggio inviato correttamente.")
        print("-> Controlla la tua chat di Telegram.")
        
    except TelegramError as e:
        print(f"\n❌ ERRORE: Impossibile inviare il messaggio. Dettagli: {e}")
        # ... (messaggi di errore come prima) ...
    except Exception as e:
        print(f"\n❌ Si è verificato un errore imprevisto: {e}")
if __name__ == "__main__":
    # -> Esegui la funzione asincrona con asyncio.run()
    asyncio.run(test_telegram_message())