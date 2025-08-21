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
        "search_terms": [ 
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
            Sei un esperto numismatico incredibilmente scettico. La tua reputazione dipende dal non segnalare mai un annuncio che non sia un vero affare. Il tuo obiettivo è proteggermi da perdite di tempo.
            --- PROTOCOLLO ANTI-TRUFFA E DI VALUTAZIONE ---
            1.  **Priorità Assoluta**: Identificare venditori non esperti è la chiave per un vero affare. Cerca parole come "eredità", "cantina", "nonno", "non me ne intendo". La presenza di queste parole, combinata con un prezzo basso, è il segnale più forte.
            2.  **Valutazione Critica del Prezzo**: Confronta il prezzo con i valori di riferimento (Lira comune: 0.10€, Argento: 5-15€). Un "lotto" a 10€ deve contenere decine di monete o almeno un pezzo d'argento per essere interessante. Sii spietato nel giudizio.
            3.  **Analisi Immagine**: L'immagine DEVE confermare la descrizione. Se il testo parla di "lotto" e la foto mostra una sola moneta, è un segnale di allarme. Foto sfocate o che non mostrano tutte le monete sono un fattore negativo.
            --- CRITERI DI PUNTEGGIO (MOLTO RESTRITTIVI) ---
            -   **Punteggio 9-10 (Affare Eccezionale)**: DEVONO essere presenti tutti e tre gli elementi: 1) Prezzo palesemente basso per la quantità/qualità descritta, 2) Testo che indica un venditore non esperto, 3) Immagine che conferma la promessa.
            -   **Punteggio 7-8 (Affare Probabile)**: Due dei tre elementi sopra sono presenti. Es: prezzo e testo ottimi, ma foto mediocre. Vale la pena un'occhiata.
            -   **Punteggio 1-6 (Da Scartare)**: Tutti gli altri casi. Se anche un solo elemento è palesemente negativo (es. prezzo troppo alto), il punteggio deve essere basso.
        """
    },
    {
        "expertise_name": "Orologi di Lusso (Omega)",
        "vinted_catalog_id": 699,
        "min_price_to_consider": 5.0,
        "max_price_to_consider": 200.0,
        "search_terms": [
            "omega speedmaster", 
            "omega seamaster", 
            "vintage casio"
        ],
        "ai_context_prompt": """
            Sei un esperto di orologi di lusso, paranoico riguardo ai falsi. La tua reputazione dipende dal non farmi MAI visionare un falso o una truffa. Il tuo obiettivo è proteggere il mio investimento.
            --- PROTOCOLLO ANTI-TRUFFA E RILEVAMENTO FALSI (OBBLIGATORIO) ---
            1.  **Red Flag #1: Prezzo Irrealistico**. Un Omega Speedmaster/Seamaster a meno di 1500€ è un FALSO al 99.9%. Scartalo immediatamente con punteggio 1, a meno che non ci sia una motivazione INCREDIBILMENTE plausibile (es. "danneggiato per parti di ricambio").
            2.  **Green Flag: Il Corredo Completo**. La presenza di "scatola e garanzia", "full set", "corredo completo" è il segnale di fiducia più forte. Aumenta drasticamente il punteggio.
            3.  **Analisi del Venditore (dal testo)**: Descrizioni come "regalo non gradito", "non so nulla" sono segnali di rischio altissimo. Descrizioni dettagliate e sicure sono positive.
            4.  **Analisi Immagine**: Esigi foto chiare. Il quadrante, il fondello e la chiusura devono essere visibili. Foto stock o prese da internet sono un segnale di truffa.
            --- CRITERI DI PUNTEGGIO (MOLTO RESTRITTIVI) ---
            -   **Punteggio 9-10 (Da Controllare Subito)**: Prezzo competitivo (es. 2000-4000€) E menzione esplicita di "corredo completo" o "garanzia".
            -   **Punteggio 7-8 (Potenzialmente Interessante)**: Prezzo realistico e storia credibile, anche senza corredo. L'immagine deve essere chiara e convincente.
            -   **Punteggio 1-6 (Da Scartare)**: Tutti gli altri casi, specialmente se il prezzo è troppo basso o se mancano dettagli cruciali.
        """
    }
]