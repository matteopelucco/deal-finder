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
INTERVALLO_INTERO_CICLO = 60

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
        "expertise_name": "Caccia ai Lotti da Eredità", 
        "vinted_catalog_id": 4895, 
        "min_price_to_consider": 5.0, 
        "max_price_to_consider": 50.0, 
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
        "expertise_name": "Argento Italiano (Repubblica)",
        "vinted_catalog_id": 4895,
        "min_price_to_consider": 5.0, 
        "max_price_to_consider": 20.0,
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
        "expertise_name": "Monete Storiche Italiane (Sottocosto)",
        "vinted_catalog_id": 4895, 
        "min_price_to_consider": 5.0, 
        "max_price_to_consider": 100.0,
        "search_terms": [ "Vittorio Emanuele", "Umberto I", "Carlo Felice", "Regno d'Italia monete", "quadriga", "monete antiche" ],
        "ai_context_prompt": """
            MISSIONE: Trovare monete del Regno d'Italia di alta qualità vendute a un prezzo visibilmente inferiore a quello di mercato, probabilmente da venditori che hanno fretta di vendere o non conoscono il valore specifico di quella conservazione.
            --- PROTOCOLLO CACCIA ALL'AFFARE ---
            1. **Qualità vs Prezzo**: Cerca l'anomalia: una moneta descritta (e mostrata) come di alta qualità (SPL, FDC) ma con un prezzo da moneta comune.
            2. **Lotti Vantaggiosi**: Un lotto di monete del Regno è interessante solo se il prezzo per singola moneta è chiaramente stracciato.
            --- PUNTEGGIO (SOLO AFFARI VERI) ---
            - **Punteggio 7-10**: SOLO per monete di alta conservazione a un prezzo da moneta comune, o lotti venduti palesemente sottocosto. Ignora gli annunci a prezzo "giusto".
        """
    },
    {
        "expertise_name": "Eurodivisionali (Prezzo Errore)",
        "vinted_catalog_id": 4895, 
        "min_price_to_consider": 10.0, 
        "max_price_to_consider": 25.0,
        "search_terms": [ "divisionale euro", "fondo specchio", "2 euro commemorativi" ],
        "ai_context_prompt": """
            MISSIONE: Identificare set della Zecca (divisionali, proof) venduti a un prezzo che non tiene conto del loro valore collezionistico, spesso da persone che le hanno ricevute in regalo.
            --- PROTOCOLLO CACCIA ALL'AFFARE ---
            1. **Cerca la Confezione**: L'affare si trova quasi sempre su prodotti in confezione ufficiale della Zecca.
            2. **Valore di Mercato Basso**: Un affare è trovare una divisionale (valore facciale < 10€) venduta a 15-20€ quando il suo valore di mercato è 40-50€.
            --- PUNTEGGIO (SOLO AFFARI VERI) ---
            - **Punteggio 7-10**: SOLO se il prezzo è palesemente inferiore al valore di mercato standard per quel set. Un 2€ commemorativo venduto a 2.50€ NON è un affare.
        """
    },
    {
        "expertise_name": "Monete d'Oro/Argento (Investimento Sotto Quotazione)",
        "vinted_catalog_id": 4895, 
        "min_price_to_consider": 20.0, 
        "max_price_to_consider": 700.0,
        "search_terms": [ "moneta d'oro", "sovereign", "Morgan dollar", "sterlina oro" ],
        "ai_context_prompt": """
            MISSIONE: Trovare monete da investimento (Oro/Argento) vendute da privati a un prezzo INFERIORE alla quotazione spot del metallo. L'unico motivo per una notifica è un'opportunità di arbitraggio finanziario.
            --- PROTOCOLLO CACCIA ALL'AFFARE ---
            1. **Autenticità SOPRA OGNI COSA**: Il minimo dubbio sull'autenticità (foto, descrizione, venditore) e l'annuncio va scartato con punteggio 1.
            2. **Prezzo vs Spot Price**: L'annuncio è un affare SOLO se il prezzo richiesto è più basso della quotazione di mercato del metallo.
            --- PUNTEGGIO (SOLO AFFARI VERI) ---
            - **Punteggio 7-10**: SOLO se l'annuncio ispira MASSIMA fiducia E il prezzo è sotto la quotazione del metallo. Altrimenti, è da scartare.
        """
    },
    {
        "expertise_name": "Banconote FDS (Sottovalutate)",
        "vinted_catalog_id": 4895, 
        "min_price_to_consider": 2.0, 
        "max_price_to_consider": 200.0,
        "search_terms": [ "banconote lire", "vecchie banconote fds" ],
        "ai_context_prompt": """
            MISSIONE: Trovare lotti o singole banconote in condizioni perfette (Fior di Stampa, FDS) vendute al prezzo di banconote circolate.
            --- PROTOCOLLO CACCIA ALL'AFFARE ---
            1. **Cerca "FDS"**: La parola chiave "FDS" o "Fior di Stampa" è fondamentale.
            2. **Verifica Visiva**: L'immagine deve confermare l'assenza assoluta di pieghe o usura.
            --- PUNTEGGIO (SOLO AFFARI VERI) ---
            - **Punteggio 7-10**: SOLO per banconote descritte e mostrate come FDS, ma con un prezzo da banconota usata.
        """
    },
    {
        "expertise_name": "Accessori (Lotti o Stock)",
        "vinted_catalog_id": 4895, 
        "min_price_to_consider": 5.0, 
        "max_price_to_consider": 60.0,
        "search_terms": [ "album monete", "raccoglitore monete", "lotto vassoi monete" ],
        "ai_context_prompt": """
            MISSIONE: Trovare lottii di accessori per collezionismo (album, raccoglitori, vassoi) venduti in blocco a un prezzo stracciato, tipicamente per cessato hobby.
            --- PROTOCOLLO CACCIA ALL'AFFARE ---
            1. **Quantità**: Cerca le parole "lotto", "stock", "tutto insieme". L'affare non è sul singolo pezzo, ma sul blocco.
            2. **Prezzo per Pezzo**: Il prezzo totale diviso per il numero di articoli deve essere irrisorio.
            --- PUNTEGGIO (SOLO AFFARI VERI) ---
            - **Punteggio 7-10**: SOLO per lotti di più articoli a un prezzo chiaramente da "svuota tutto".
        """
    },
    {
        "expertise_name": "Caccia agli Omega", 
        "vinted_catalog_id": 699,
        "min_price_to_consider": 10.0,  
        "max_price_to_consider": 300.0, 
        "search_terms": [
            "orologio cronografo nonno",
            "orologio omega eredità",
            "vecchio orologio omega",
            "lotto orologi"
        ],
        "ai_context_prompt": """
            Sei un "detective del valore nascosto", specializzato nel trovare orologi Omega di lusso venduti da persone completamente ignare del loro valore. Il tuo unico obiettivo è individuare annunci in cui un vero Omega Speedmaster o Seamaster viene venduto a un prezzo ridicolmente basso perché scambiato per un normale orologio vecchio.
            --- PROTOCOLLO DI RILEVAMENTO ANOMALIE (OBBLIGATORIO) ---
            1.  **L'Anomalia Prezzo/Testo (Priorità #1)**: Cerca la combinazione esplosiva di un PREZZO MOLTO BASSO (< 1000€) e un TESTO che indica ignoranza totale. Parole come "nonno", "soffitta", "eredità", "non funziona", "non so se è originale", "vendo come visto e piaciuto" sono ORO PURO.
            2.  **Identificazione Visiva (Il Lavoro da Detective)**: Poiché il venditore potrebbe non scrivere "Speedmaster", devi riconoscerlo dalla foto. Cerca le caratteristiche iconiche:
                -   **Speedmaster**: Tre contatori sul quadrante (a ore 3, 6, 9), scala tachimetrica sulla lunetta esterna.
                -   **Seamaster (Diver)**: Lancette scheletrate, valvola dell'elio a ore 10.
                Anche se l'immagine è di bassa qualità, se riesci a intravedere queste caratteristiche, l'interesse è altissimo.
            3.  **Il Corredo Inaspettato**: Se un annuncio con testo da inesperti e prezzo basso menziona anche una "scatola vecchia" o "vecchi fogli", è un jackpot potenziale.
            --- CRITERI DI PUNTEGGIO (CACCIA AL TESORO) ---
            -   **Punteggio 9-10 (JACKPOT POTENZIALE)**: Annuncio con testo che indica chiaramente ignoranza ("orologio del nonno") E prezzo inferiore a 1000€ E una foto in cui SI INTRAVEDONO le caratteristiche di uno Speedmaster/Seamaster. Questa è una notifica di massima urgenza.
            -   **Punteggio 7-8 (Anomalia Interessante)**: Prezzo basso e testo da inesperto, ma la foto è troppo brutta per confermare il modello. O, viceversa, la foto mostra un Omega ma il prezzo è un po' più alto (es. 1200€) e il testo è ambiguo.
            -   **Punteggio 1-6 (Falso Allarme)**: Tutti gli altri casi. Se sembra un normale orologio vintage, un cronografo non di marca, o se il prezzo è comunque realistico, non è il tesoro che cerchiamo.
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