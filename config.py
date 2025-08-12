import os
from dotenv import load_dotenv
# Carica le variabili dal file .env nella sessione corrente
load_dotenv()
# --- CONFIGURAZIONI UTENTE CARICATE DALL'AMBIENTE ---
# Legge il token del bot dal file .env
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# Legge il Chat ID dal file .env
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# Legge la chiave API di OpenAI dal file .env
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Lista delle ricerche da effettuare su Vinted
SEARCH_TERMS = [
    "monete eredità",
    "vecchie monete",
    "monete nonno",
    "lotto monete euro",
    "monete miste",
    "500 lire argento",
    "2 euro commemorativi lotto",
    "monete collezione",
    "monete Regno d’Italia",
    "vecchie lire"
]
# Intervallo di attesa tra una scansione completa e l'altra (in secondi)
# 1800 secondi = 30 minuti
WAIT_TIME_SECONDS = 60