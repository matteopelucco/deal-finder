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
    "vecchie monete",
    "monete nonno",
    "scatola monete",
    "monete antiche",
    "monete miste",
    "500 lire argento",
    "monete collezione",
    "monete Regno d’Italia",
    "vecchie lire"
]

# Intervallo di attesa tra una scansione completa e l'altra (in secondi)
# 1800 secondi = 30 minuti
INTERVALLO_ORARIO = 3600

# Numero massimo di annunci da considerare per ogni termine di ricerca ad ogni ciclo.
# Limita il numero di risultati presi dallo scraper per l'analisi.
MAX_ANNUNCI_DA_CONSIDERARE = 10

# Numero massimo di file da conservare nella memoria persistita
MAX_HISTORY_SIZE = 400  # -> Dimensione massima della nostra cronologia

# Categoria
VINTED_CATALOG = "4895"

# Timeout in secondi per le richieste web dello scraper.
SCRAPER_TIMEOUT_SECONDS = 30

# Intervallo tra un termine di ricerca e il seguente
INTERVALLO_INTRA_TERMS = 30

# Intervallo tra una scansione di un annuncio e la seguente
INTERVALLO_INTRA_ARTICLES = 15