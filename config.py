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

# Timeout in secondi per le richieste web dello scraper.
SCRAPER_TIMEOUT_SECONDS = 20

# Intervallo tra un termine di ricerca e il seguente
INTERVALLO_INTRA_TERMS = 15

# Intervallo tra una scansione di un annuncio e la seguente
INTERVALLO_INTRA_ARTICLES = 15

# Salta l'analisi per tutti gli annunci con un prezzo uguale o inferiore a questo valore.
# Utile per scartare annunci con prezzi placeholder (es. 1€).
PREZZO_MINIMO_DA_CONSIDERARE = 1.0
PREZZO_MASSIMO_DA_CONSIDERARE = 120.0

# ==============================================================================
# --- NUOVA CONFIGURAZIONE ASTRATTA DEI TARGET DI RICERCA ---
# ==============================================================================
# Ogni dizionario in questa lista rappresenta un "target" che il bot cercherà.
# Per aggiungere un nuovo tipo di affare (es. borse, videogiochi), basta
# aggiungere un nuovo dizionario qui, senza toccare il codice principale.
SEARCH_TARGETS = [
    {
        "expertise_name": "Numismatica", # Nome identificativo per il log
        "vinted_catalog_id": 4895,
        "min_price_to_consider": 2.0,
        "max_price_to_consider": 150.0,
        "search_terms": [ # -> Ora è una lista
            "monete argento",
            "vecchie monete",
            "monete nonno",
            "scatola monete",
            "monete antiche",
            "monete miste",
            "500 lire argento",
            "monete collezione",
            "monete Regno d’Italia",
            "vecchie lire"

        ],
        "ai_context_prompt": """
            Sei un esperto numismatico molto critico e selettivo.
            --- REGOLE DI VALUTAZIONE (MONETE) ---
            1.  Confronta il prezzo con il valore di mercato. Un lotto con argento a basso costo è un affare.
            2.  Valori di riferimento: Lira comune = 0.10€, Moneta argento = 5-15€, 2€ comm. = 3€.
            3.  Indicatori di affare: parole come "eredità", "nonno", "cantina", "non me ne intendo".
            --- CRITERI DI PUNTEGGIO (MONETE) ---
            -   Punteggio 8-10 (Affare Imperdibile): Prezzo palesemente basso per un lotto con argento o monete antiche, da venditore non esperto.
            -   Punteggio 1-4 (Da Scartare): Prezzo alto, singole monete comuni.
        """
    },
    {
        "expertise_name": "Orologi di Lusso (Omega)",
        "vinted_catalog_id": 699,
        "min_price_to_consider": 5.0,
        "max_price_to_consider": 200.0,
        "search_terms": [ # -> Ora è una lista
            "omega speedmaster", 
            "omega seamaster"
        ],
        "ai_context_prompt": """
            Sei un esperto di orologi di lusso, specializzato in Omega, molto attento alle truffe.
            --- REGOLE DI VALUTAZIONE (OROLOGI OMEGA) ---
            1.  La priorità è l'AUTENTICITÀ. Un prezzo troppo basso (< 1500€) è un enorme segnale di allarme per un falso.
            2.  Valore di mercato di riferimento: uno Speedmaster usato parte da 2500-3000€ e sale.
            3.  Indicatori di autenticità: parole come "corredo completo", "scatola e garanzia", "acquistato da concessionario".
            4.  Indicatori di rischio: "nessuna scatola", "regalo non gradito", descrizioni vaghe.
            --- CRITERI DI PUNTEGGIO (OROLOGI OMEGA) ---
            -   Punteggio 8-10 (Affare Potenziale): Prezzo competitivo (es. 2000-3000€) CON corredo completo e storia credibile.
            -   Punteggio 5-7 (Da Verificare): Prezzo interessante ma senza corredo. Rischio più alto.
            -   Punteggio 1-4 (Da Scartare): Prezzo irrealisticamente basso (probabile truffa) o troppo alto.
        """
    }
]