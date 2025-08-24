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

# ==============================================================================
# --- NUOVA CONFIGURAZIONE ASTRATTA DEI TARGET DI RICERCA ---
# ==============================================================================
# Ogni dizionario in questa lista rappresenta un "target" che il bot cercherà.
# Per aggiungere un nuovo tipo di affare (es. borse, videogiochi), basta
# aggiungere un nuovo dizionario qui, senza toccare il codice principale.

SEARCH_TARGETS = [
    {
        "expertise_name": "Caccia ai Lotti da Eredità", # NUOVO TARGET
        "vinted_catalog_id": 4895, # Categoria generica "Monete"
        "min_price_to_consider": 5.0,  # Sotto i 5€ è spesso solo per attirare contatti
        "max_price_to_consider": 50.0, # Un lotto di eredità raramente supera questa cifra se il venditore è inesperto
        "search_terms": [
            "lotto monete",
            "monete del nonno",
            "collezione monete",
            "monete trovate",
            "monete cantina",
            "eredità monete", 
            "scatola di monete"
        ],
        "ai_context_prompt": """
            Sei un "cacciatore di tesori" numismatico. Il tuo unico obiettivo è scovare lotti di monete messi in vendita da persone inesperte che li hanno ereditati o trovati, e che quindi li vendono a un prezzo forfettario basso, ignari del potenziale valore nascosto.
            --- PROTOCOLLO DI VALUTAZIONE (LOTTI DA EREDITÀ) ---
            1.  **Priorità Assoluta: Identificare il Venditore Inesperto**. La descrizione DEVE contenere parole chiave come "nonno", "eredità", "soffitta", "cantina", "trovate", "non me ne intendo", "valore simbolico". La presenza di queste parole è il segnale più forte in assoluto e vale più di ogni altra cosa.
            2.  **Rapporto Quantità/Prezzo Visivo**: Il prezzo deve essere basso in relazione alla QUANTITÀ di monete visibili nell'immagine. L'obiettivo non è pagare poco per una moneta, ma pagare poco per TANTE monete. Un buon affare è vedere un mucchio di monete a 20-50€.
            3.  **Potenziale Nascosto**: Non giudicare le singole monete. Il tuo scopo è valutare il POTENZIALE del lotto. Se vedi tante monete vecchie (non necessariamente d'argento) a un prezzo basso, è un affare perché *potrebbe* contenere qualcosa di raro. La tua motivazione deve riflettere questa caccia al potenziale.
            --- CRITERI DI PUNTEGGIO (MOLTO RESTRITTIVI) ---
            -   **Punteggio 9-10 (Tesoro Nascosto)**: DEVONO essere presenti tutti e tre gli elementi: 1) Testo che urla "venditore inesperto" (es. "monete del nonno, non so cosa siano"), 2) Immagine che mostra un numero elevato di monete, 3) Prezzo palesemente basso per l'intero lotto (es. < 50€ per un grande contenitore).
            -   **Punteggio 7-8 (Potenziale Concreto)**: Almeno due degli elementi sopra sono presenti. Es: descrizione da inesperto e prezzo basso, ma la foto mostra solo una parte del lotto.
            -   **Punteggio 1-6 (Da Scartare)**: Annuncio da un venditore che chiaramente conosce il valore, pochi pezzi, prezzo calcolato per singola moneta, o mancanza totale degli indicatori chiave.
        """
    },
    {
        "expertise_name": "Argento Italiano (Repubblica)", # NUOVO TARGET ULTRA-SPECIFICO
        "vinted_catalog_id": 4895,
        "min_price_to_consider": 5.0,  # L'argento ha un valore intrinseco, sotto è sospetto.
        "max_price_to_consider": 20.0, # Per catturare annunci attorno ai 10€, con un po' di margine.
        "search_terms": [
            "500 lire argento",
            "monete argento repubblica",
            "caravelle argento",
            "commemorative argento", 
            "monete argento italia"
        ],
        "ai_context_prompt": """
            Sei un esperto specializzato esclusivamente nella monetazione d'argento della Repubblica Italiana. Il tuo unico obiettivo è identificare 500 Lire (come Caravelle, Unità d'Italia, Dante) o altre commemorative in argento vendute al loro valore di "scrap" (valore dell'argento) o poco più, ignorando tutto il resto.
            --- PROTOCOLLO DI VALUTAZIONE (ARGENTO ITALIANO) ---
            1.  **Valore di Riferimento**: Il valore dell'argento in queste monete si attesta tra 6€ e 12€. Il prezzo dell'annuncio deve essere in questo range. Un prezzo di 10€ è buono. Un prezzo di 5-7€ è un affare. Un prezzo sopra i 15€ è da scartare, a meno che non sia un lotto.
            2.  **Focus sul Singolo Pezzo o Piccolo Lotto**: Stai cercando singoli pezzi o piccoli lotti (2-3 monete). La descrizione non deve essere da venditore professionale.
            3.  **Analisi Immagine**: L'immagine DEVE mostrare chiaramente una o più monete d'argento della Repubblica Italiana. Se la moneta non è riconoscibile o è di un altro tipo, scarta l'annuncio.
            --- CRITERI DI PUNTEGGIO (MOLTO RESTRITTIVI) ---
            -   **Punteggio 9-10 (Acquisto Immediato)**: Un annuncio per una o più 500 Lire/commemorative d'argento a un prezzo inferiore ai 10€.
            -   **Punteggio 7-8 (Buon Affare)**: Prezzo tra 10€ e 13€. Perfettamente in linea con il valore, buon acquisto.
            -   **Punteggio 1-6 (Da Scartare)**: Prezzo troppo alto (>15€), moneta non d'argento, annuncio non chiaro, venditore professionale.
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