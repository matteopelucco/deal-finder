import os
from dotenv import load_dotenv

# Carica le variabili dal file .env nella sessione corrente
load_dotenv()

# --- CONFIGURAZIONI UTENTE CARICATE DALL'AMBIENTE ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Intervallo di attesa tra una scansione completa e l'altra (in secondi)
# 1800 secondi = 30 minuti
INTERVALLO_INTERO_CICLO = 600

# Numero massimo di annunci da considerare per ogni termine di ricerca ad ogni ciclo.
# Limita il numero di risultati presi dallo scraper per l'analisi.
MAX_ANNUNCI_DA_CONSIDERARE = 20

# Numero massimo di file da conservare nella memoria persistita
MAX_HISTORY_SIZE = 2000

# Timeout in secondi per le richieste web dello scraper.
SCRAPER_TIMEOUT_SECONDS = 20

# Intervallo tra un termine di ricerca e il seguente
INTERVALLO_INTRA_TERMS = 15

# Intervallo tra una scansione di un annuncio e la seguente
INTERVALLO_INTRA_ARTICLES = 15

# ==============================================================================
# --- MODALITÀ DI DEBUG PER LO SCRAPER ---
# Se impostato a True, lo scraper salverà l'HTML grezzo di ogni pagina di ricerca 
# in un file nella cartella 'debug_logs/'. Questo è estremamente utile per
# diagnosticare problemi con i selettori CSS.
# Impostalo a False per le operazioni normali.
# ==============================================================================
DEBUG_SCRAPER_HTML = False

TRIAGE_AI_PROMPT = """
    Sei un'intelligenza artificiale da triage, ultra-veloce ed efficiente. Il tuo unico scopo è decidere se un annuncio merita un'analisi più approfondita e costosa. Non devi essere perfetto, devi solo scartare gli annunci palesemente inutili, come si comporterebbe un essere umano che scorrendo un elenco di risultati, decide di cliccarne uno ed esplorarne descrizione e immagini solo basandosi sulla propria intuzione.
    --- PROTOCOLLO DI TRIAGE RAPIDO ---
    1.  **Anomalia Prezzo/Titolo**: Cerca un'incongruenza. Se il titolo contiene parole come "lotto", "collezione", "eredità" e il prezzo è basso, è un segnale forte. Se menziona un marchio di lusso (es. "Omega") e il prezzo è molto basso, è un segnale forte.
    2.  **Potenziale Visivo**: Guarda l'immagine. Se mostra una grande quantità di oggetti o un pezzo che sembra di alta qualità nonostante il prezzo basso, è un segnale forte.
    3.  **Scarta il "Normale"**: Se un annuncio sembra normale (es. "moneta da 2 euro" a 3€), scartalo. Stiamo cercando articolo interessanti e potenzialmente "affari".
    Basandoti SOLO su titolo, prezzo e immagine, rispondi ESCLUSIVAMENTE con un oggetto JSON con questa struttura:
    {"continua_analisi": boolean, "motivazione": "stringa"}
    - "continua_analisi": true SOLO se individui un segnale forte che suggerisce un potenziale affare.
    - "motivazione": Spiega in 2-5 parole il motivo della tua decisione (es. "prezzo normale", "lotto interessante", "foto non chiara", "sembra un affare").
"""
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
        "max_price_to_consider": 250.0,
        "search_terms": [
            "lotto monete",
            "monete nonno",
            "collezione monete",
            "monete trovate",
            "eredità monete",
            "vecchie lire",
            "vecchie monete",
            "monete miste"
        ],
        "ai_context_prompt": 
            "MISSIONE: Identificare lotti di monete venduti da persone totalmente ignare del loro valore. "
            "L'obiettivo è l'acquisto speculativo, cercando il tesoro nascosto."
            "--- PROTOCOLLO CACCIA ALL'AFFARE ---"
            "0. **VERIFICA PRELIMINARE (OBBLIGATORIA)**: Assicurati che l'annuncio riguardi ESCLUSIVAMENTE monete o banconote. Se l'immagine o la descrizione mostrano gioielli, medaglie, lingotti, orologi o altri oggetti non numismatici, assegna immediatamente un punteggio di 1 e nella motivazione scrivi 'Annuncio non pertinente'."
            "1. **Analisi del Venditore (Critico!)**: Il numero di recensioni è fondamentale. Un venditore con poche recensioni (< 20) che usa parole come \"nonno\" o \"eredità\" è il target perfetto. Un venditore con molte recensioni (> 250) è quasi certamente un commerciante; scartalo a meno che il prezzo non sia palesemente un errore."
            "2. **Indicatore Testuale**: Cerca ossessivamente parole come \"nonno\", \"soffitta\", \"non so cosa siano\". Se dette da un venditore con poche recensioni, l'interesse è massimo."
            "3. **Indicatore Prezzo/Quantità**: Il prezzo deve essere illogico per la quantità. 20€ per una scatola piena, 50€ per un album intero."
            "--- PUNTEGGIO (SOLO AFFARI VERI) ---"
            "- **Punteggio 7-10**: SOLO se l'annuncio è pertinente E ci sono chiari indicatori di venditore inesperto E il prezzo è palesemente basso per la quantità mostrata. Qualsiasi altra cosa è da scartare."
    },
    {
        "expertise_name": "Caccia a Monete d'Oro (Sottocosto)",
        "vinted_catalog_id": 4895,
        "min_price_to_consider": 55.0,
        "max_price_to_consider": 1200.0,
        "search_terms": [
            "marengo oro",
            "moneta d'oro",
            "vreneli",
            "sterlina oro",
            "sovereign", 
            "moneta dorata"
        ],
        "ai_context_prompt": "MISSIONE: Identificare monete d'oro ufficiali (Marengo, Sterline, Vreneli, etc.) vendute da privati inesperti a un prezzo significativamente inferiore al loro valore intrinseco. Massima allerta per le truffe."
        "--- PROTOCOLLO CACCIA AL TESORO D'ORO ---"
        "0. **VERIFICA PRELIMINARE (OBBLIGATORIA)**: Assicurati che l'annuncio sia per una MONETA D'ORO. Se mostra lingotti, gioielli, medaglie o monete placcate, assegna immediatamente un punteggio di 1 e nella motivazione scrivi 'Annuncio non pertinente'."
        "1. **Analisi del Venditore (Critico per le Truffe!)**: La combinazione di un oggetto di alto valore e un venditore nuovo è il più grande segnale di allarme. Un venditore con 0-10 recensioni che vende una moneta d'oro è da considerare estremamente rischioso. La massima fiducia va a venditori con poche recensioni (< 50) che usano un linguaggio da \"eredità\"."
        "2. **Analisi del Prezzo (Formula dell'Affare)**: L'oro vale circa 95€/grammo. Stiamo cercando un prezzo target inferiore a 75€/grammo. Un Marengo (circa 5.8g di oro puro) dovrebbe valere ~550€. Un affare eccezionale è sotto i 450€. Usa questa logica: se il prezzo è troppo basso per essere vero (es. 100€ per un Marengo), è una truffa al 99%. Se è basso ma plausibile (350-450€), è il nostro target."
        "3. **Indicatore Testuale dell'Inesperienza**: Cerca attivamente parole come \"nonno\", \"eredità\", \"trovata in un cassetto\", \"non me ne intendo\". Questa è la giustificazione più forte per un prezzo basso e un annuncio legittimo."
        "--- PUNTEGGIO (SOLO AFFARI VERI) ---"
        "- **Punteggio 9-10 (JACKPOT)**: Annuncio con testo che indica chiaramente ignoranza (\"moneta del nonno\") E prezzo plausibilmente basso (es. 350-450€ per un Marengo) E un venditore con un numero di recensioni basso ma non nullo (es. 5-30 recensioni)."
        "- **Punteggio 7-8 (Affare Potenziale)**: Prezzo basso ma venditore con molte recensioni (potrebbe essere un professionista che svende) o testo vago. Richiede attenzione."
        "- **Punteggio 1-6 (Da Scartare)**: Prezzo troppo basso per essere vero, venditore con 0 recensioni, annuncio da commerciante a prezzo di mercato, annuncio non pertinente."
    },
    {
        "expertise_name": "Argento Italiano (al Peso)",
        "vinted_catalog_id": 4895,
        "min_price_to_consider": 5.0,
        "max_price_to_consider": 250.0,
        "search_terms": [
            "500 lire argento",
            "caravelle argento",
            "argento commemorativo"
        ],
        "ai_context_prompt": "MISSIONE: Acquistare monete d'argento della Repubblica Italiana a un prezzo uguale o INFERIORE al solo valore del metallo. È una pura operazione finanziaria."
        "--- PROTOCOLLO CACCIA ALL'AFFARE ---"
        "0. **VERIFICA PRELIMINARE (OBBLIGATORIA)**: Assicurati che l'annuncio riguardi ESCLUSIVAMENTE monete o banconote. Se l'immagine o la descrizione mostrano gioielli, medaglie, posate, lingotti o altri oggetti in argento, assegna immediatamente un punteggio di 1 e nella motivazione scrivi 'Annuncio non pertinente'."
        "1. **Analisi del Venditore**: Un venditore professionale con molte recensioni difficilmente venderà sotto il valore del metallo. Presta più attenzione agli annunci di venditori con poche recensioni."
        "2. **Valore Target**: Il valore dell'argento di una 500 Lire è circa 8-10€. L'annuncio è un affare SOLO se il prezzo è <= 10€."
        "--- PUNTEGGIO (SOLO AFFARI VERI) ---"
        "- **Punteggio 9-10 (Acquisto Immediato)**: Prezzo ≤ 8€."
        "- **Punteggio 7-8 (Buon Acquisto)**: Prezzo tra 8€ e 10€."
        "- **Sotto il 7**: Qualsiasi prezzo superiore a 10€ o annuncio non pertinente."
    },
    {
        "expertise_name": "Monete Storiche Italiane (Sottocosto)",
        "vinted_catalog_id": 4895,
        "min_price_to_consider": 5.0,
        "max_price_to_consider": 250.0,
        "search_terms": [
            "Vittorio Emanuele",
            "Umberto I",
            "Carlo Felice",
            "Regno d'Italia monete",
            "quadriga",
            "monete antiche"
        ],
        "ai_context_prompt": "MISSIONE: Trovare monete del Regno d'Italia di alta qualità vendute a un prezzo visibilmente inferiore a quello di mercato."
        "--- PROTOCOLLO CACCIA ALL'AFFARE ---"
        "0. **VERIFICA PRELIMINARE (OBBLIGATORIA)**: Assicurati che l'annuncio riguardi ESCLUSIVAMENTE monete o banconote. Se vedi medaglie militari, gettoni, o altri oggetti storici non monetari, assegna un punteggio di 1 e nella motivazione scrivi 'Annuncio non pertinente'."
        "1. **Analisi del Venditore**: Un venditore con molte recensioni e molti articoli simili è un professionista. La probabilità di un affare è bassa. Un venditore con poche recensioni è un target migliore."
        "2. **Qualità vs Prezzo**: Cerca l'anomalia: una moneta di alta qualità visibile in foto ma con un prezzo da moneta comune."
        "--- PUNTEGGIO (SOLO AFFARI VERI) ---"
        "- **Punteggio 7-10**: SOLO per monete pertinenti, di alta conservazione e a un prezzo da affare. Ignora gli annunci a prezzo \"giusto\" di venditori professionali."
    },
    {
        "expertise_name": "Eurodivisionali (Prezzo Errore)",
        "vinted_catalog_id": 4895,
        "min_price_to_consider": 5.0,
        "max_price_to_consider": 250.0,
        "search_terms": [
            "divisionale euro",
            "fondo specchio",
            "2 euro commemorativi"
        ],
        "ai_context_prompt": "MISSIONE: Identificare set della Zecca (divisionali, proof) venduti a un prezzo che non tiene conto del loro valore collezionistico."
        "--- PROTOCOLLO CACCIA ALL'AFFARE ---"
        "0. **VERIFICA PRELIMINARE (OBBLIGATORIA)**: Assicurati che si tratti di monete a corso legale. Se l'annuncio mostra medaglie-souvenir, gettoni o altre \"monete\" non ufficiali, assegna un punteggio di 1 e nella motivazione scrivi 'Annuncio non pertinente'."
        "1. **Analisi del Venditore**: Un venditore con poche recensioni che vende una divisionale a 20€ è molto più interessante di un negozio."
        "2. **Cerca la Confezione**: L'affare si trova quasi sempre su prodotti in confezione ufficiale della Zecca."
        "--- PUNTEGGIO (SOLO AFFARI VERI) ---"
        "- **Punteggio 7-10**: SOLO se il prezzo è palesemente inferiore al valore di mercato standard per quel set, preferibilmente da un venditore con poche recensioni."
    },
    {
        "expertise_name": "Monete d'Oro/Argento (Investimento Sotto Quotazione)",
        "vinted_catalog_id": 4895,
        "min_price_to_consider": 5.0,
        "max_price_to_consider": 2500.0,
        "search_terms": [
            "moneta d'oro",
            "sovereign",
            "Morgan dollar",
            "sterlina oro"
        ],
        "ai_context_prompt": "MISSIONE: Trovare monete da investimento (Oro/Argento) vendute da privati a un prezzo INFERIORE alla quotazione spot del metallo. Massima allerta per le truffe."
        "--- PROTOCOLLO CACCIA ALL'AFFARE ---"
        "0. **VERIFICA PRELIMINARE (OBBLIGATORIA)**: L'annuncio deve riguardare una MONETA ufficiale. Se l'oggetto è un lingotto, una medaglia, un gioiello o un dente d'oro, assegna un punteggio di 1 e nella motivazione scrivi 'Annuncio non pertinente'."
        "1. **Analisi del Venditore (Critico!)**: Un venditore con 0 recensioni è un RED FLAG. L'affidabilità (>50 recensioni) è un requisito non negoziabile."
        "2. **Autenticità SOPRA OGNI COSA**: Il minimo dubbio sull'autenticità (foto, descrizione) e l'annuncio va scartato."
        "--- PUNTEGGIO (SOLO AFFARI VERI) ---"
        "- **Punteggio 7-10**: SOLO se l'annuncio è pertinente, il venditore è affidabile E il prezzo è sotto la quotazione del metallo."
    },
    {
        "expertise_name": "Banconote FDS (Sottovalutate)",
        "vinted_catalog_id": 4895,
        "min_price_to_consider": 2.0,
        "max_price_to_consider": 200.0,
        "search_terms": [
            "banconote lire",
            "vecchie banconote fds"
        ],
        "ai_context_prompt": "MISSIONE: Trovare lotti o singole banconote in condizioni perfette (Fior di Stampa, FDS) vendute al prezzo di banconote circolate."
        "--- PROTOCOLLO CACCIA ALL'AFFARE ---"
        "0. **VERIFICA PRELIMINARE (OBBLIGATORIA)**: L'annuncio deve essere per banconote. Se l'immagine mostra monete, assegni, francobolli o altro, assegna un punteggio di 1 e scrivi 'Annuncio non pertinente'."
        "1. **Analisi del Venditore**: Un venditore non specializzato con poche recensioni ha più probabilità di sottovalutare una banconota FDS."
        "2. **Cerca \"FDS\"**: La parola chiave \"FDS\" o \"Fior di Stampa\" è fondamentale."
        "--- PUNTEGGIO (SOLO AFFARI VERI) ---"
        "- **Punteggio 7-10**: SOLO per banconote pertinenti, descritte e mostrate come FDS, ma con un prezzo da banconota usata."
    },
    {
        "expertise_name": "Accessori (Lotti o Stock)",
        "vinted_catalog_id": 4895,
        "min_price_to_consider": 5.0,
        "max_price_to_consider": 100.0,
        "search_terms": [
            "album monete",
            "raccoglitore monete",
            "lotto vassoi monete"
        ],
        "ai_context_prompt": "MISSIONE: Trovare lotti di accessori per collezionismo (album, raccoglitori, vassoi) venduti in blocco a un prezzo stracciato, tipicamente per cessato hobby."
        "--- PROTOCOLLO CACCIA ALL'AFFARE ---"
        "0. **VERIFICA PRELIMINARE (OBBLIGATORIA)**: Assicurati che l'annuncio riguardi accessori VUOTI. Se gli album o i raccoglitori contengono monete, l'annuncio appartiene a un'altra categoria di ricerca. In tal caso, assegna punteggio 1 e scrivi 'Annuncio non pertinente (contiene monete)'."
        "1. **Analisi del Venditore**: Un venditore con poche recensioni che vende \"tutto insieme\" è il target ideale."
        "2. **Quantità**: Cerca le parole \"lotto\", \"stock\", \"cessato hobby\"."
        "--- PUNTEGGIO (SOLO AFFARI VERI) ---"
        "- **Punteggio 7-10**: SOLO per lotti di accessori vuoti a un prezzo chiaramente da \"svuota tutto\"."
    },
    {
        "expertise_name": "Omega Nascosti (Eredità)",
        "vinted_catalog_id": 699,
        "min_price_to_consider": 10.0,
        "max_price_to_consider": 250.0,
        "search_terms": [
            "orologio cronografo nonno",
            "orologio omega eredità",
            "vecchio orologio omega",
            "lotto orologi"
        ],
        "ai_context_prompt": "MISSIONE: Individuare orologi Omega di lusso venduti da persone totalmente ignare del loro valore a un prezzo ridicolmente basso."
        "--- PROTOCOLLO DI RILEVAMENTO ANOMALIE ---"
        "0. **VERIFICA PRELIMINARE (OBBLIGATORIA)**: L'annuncio deve mostrare un orologio da polso. Se mostra orologi da tasca, da parete, o gioielli, assegna punteggio 1 e scrivi 'Annuncio non pertinente'."
        "1. **Analisi del Venditore (Critico!)**: Il venditore DEVE avere poche recensioni (<20). Se ha molte recensioni, è una truffa al 99%. Scarta."
        "2. **Anomalia Prezzo/Testo**: Cerca un prezzo molto basso (< 1000€) e un testo che indica ignoranza totale (\"orologio del nonno\")."
        "3. **Identificazione Visiva**: Devi riconoscere un Omega (Speedmaster/Seamaster) dalla foto."
        "--- PUNTEGGIO (CACCIA AL TESORO) ---"
        "- **Punteggio 7-10 (JACKPOT POTENZIALE)**: SOLO se è un orologio da polso, il venditore ha poche recensioni, il testo indica ignoranza E la foto mostra un Omega riconoscibile."
    },
    {
        "expertise_name": "Orologi Omega (Mercato Standard)",
        "vinted_catalog_id": 699,
        "min_price_to_consider": 10.0,
        "max_price_to_consider": 250.0,
        "search_terms": [
            "omega speedmaster",
            "omega seamaster"
        ],
        "ai_context_prompt": "MISSIONE: Trovare un Omega autentico a un buon prezzo da un venditore affidabile nel mercato standard."
        "--- PROTOCOLLO DI VERIFICA ---"
        "0. **VERIFICA PRELIMINARE (OBBLIGATORIA)**: L'annuncio deve essere per un orologio Omega. Se l'annuncio principale è per un altro marchio o per accessori (cinturini, scatole vuote), assegna punteggio 1 e scrivi 'Annuncio non pertinente'."
        "1. **Analisi del Venditore (Critico!)**: Il venditore DEVE essere affidabile (>50 recensioni). Un venditore con 0 recensioni è un red flag."
        "2. **Priorità: Autenticità**. Il corredo completo (\"full set\") è il più grande segnale di fiducia."
        "--- PUNTEGGIO (MERCATO STANDARD) ---"
        "- **Punteggio 7-10 (Buon Affare Verificato)**: Prezzo competitivo E forti indicatori di fiducia (venditore affidabile, corredo, foto chiare)."
    }
]