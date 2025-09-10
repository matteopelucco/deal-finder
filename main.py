import asyncio
import datetime
import os
from collections import deque
import json
import logging
from log_utils.helper import LogHelper

log_handler = LogHelper.generate_color_handler()
logging.basicConfig(handlers=[log_handler], level=logging.INFO)
logger = logging.getLogger(__name__)

from config import SEARCH_TARGETS, MAX_HISTORY_SIZE, MAX_ANNUNCI_DA_CONSIDERARE, INTERVALLO_INTERO_CICLO, INTERVALLO_INTRA_ARTICLES, INTERVALLO_INTRA_TERMS, OVERRIDE_NIGHT_SHIFT
from scraper_selenium import scrap_vinted, scrap_dettagli_annuncio
from analyzer import doTriage, doCompleteArticleAnalysis
from notifier import invia_notifica

# --- GESTIONE DELLA CRONOLOGIA PERSISTENTE ---
HISTORY_FILE = "analyzed_listings.txt"

# --- NUOVA FUNZIONE DI LOGGING PER GLI ARTICOLI SCARTATI ---
# Scrive l'URL di un articolo scartato e la sua motivazione in un file di log specifico.
# Usa la modalità 'a' (append) per aggiungere righe senza cancellare il file.
def log_scarto(nome_file: str, url: str, motivazione: str):
    try:
        with open(nome_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] URL: {url} | MOTIVO: {motivazione}")
    except Exception as e:
        logger.error(f"Errore durante la scrittura del file di log '{nome_file}': {e}")

# Carica la cronologia degli annunci già analizzati da un file di testo.
# Usa un set per ricerche veloci O(1) e una deque a dimensione fissa per gestire il limite.
def carica_cronologia():
    
    if not os.path.exists(HISTORY_FILE):
        return set(), deque(maxlen=MAX_HISTORY_SIZE)
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            cronologia_deque = deque(lines, maxlen=MAX_HISTORY_SIZE)
            cronologia_set = set(cronologia_deque)
            return cronologia_set, cronologia_deque
    except Exception as e:
        logger.error(f"Errore nel caricamento della cronologia: {e}. Ripartenza con cronologia vuota.")
        return set(), deque(maxlen=MAX_HISTORY_SIZE)

def salva_cronologia(cronologia_deque: deque):
    """Salva l'intero stato della deque nel file, sovrascrivendolo."""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cronologia_deque))
    except Exception as e:
        logger.error(f"Errore nel salvataggio della cronologia: {e}")


# Ciclo principale del bot. Gestisce i target di expertise, esegue le ricerche,
# filtra i risultati, orchestra l'analisi AI e invia le notifiche.
async def main_loop():
    
    annunci_gia_analizzati_set, cronologia_deque = carica_cronologia()
    logger.info(f"Caricati {len(annunci_gia_analizzati_set)} annunci dalla cronologia (capienza massima: {MAX_HISTORY_SIZE}).")

    while True:
        ora_corrente = datetime.datetime.now().hour
        
        # Il bot è attivo solo in questa finestra oraria

        min_hour = 7
        max_hour = 23

        if OVERRIDE_NIGHT_SHIFT: 
            min_hour = -1
            max_hour = 25

        if min_hour <= ora_corrente <= max_hour:
            logger.info(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Orario di attività. Inizio nuova scansione...")
            
            # --- CICLO ESTERNO SUI CAMPI DI EXPERTISE ---
            for target in SEARCH_TARGETS:
                expertise_name = target["expertise_name"]
                catalog_id = target["vinted_catalog_id"]
                min_price = target["min_price_to_consider"]
                max_price = target["max_price_to_consider"]
                ai_context = target["ai_context_prompt"]
                search_terms = target["search_terms"]

                triage_prompt_specifico = target["triage_prompt"]

                logger.info(f"--- Inizio Scansione Expertise: '{expertise_name}' ---")

                # --- CICLO INTERNO SUI TERMINI DI RICERCA DI QUESTA EXPERTISE ---
                for term in search_terms:
                    logger.info(f"Ricerca per il termine: '{term}' per Expertise '{expertise_name}' - (Catalogo: {catalog_id})")
                    
                    risultati_scraper = scrap_vinted(term, catalog_id)
                    annunci_da_considerare = risultati_scraper[:MAX_ANNUNCI_DA_CONSIDERARE]
                    logger.info(f"Trovati {len(risultati_scraper)} annunci, ne considero i primi {len(annunci_da_considerare)}.")

                    for i, annuncio in enumerate(annunci_da_considerare, start=1):
                        
                        price = annuncio['price']
                        link = annuncio['link']
                        title = annuncio['title']
                        img_url = annuncio['img_url']
                        url = annuncio['url']

                        logger.info(f"Annuncio {i}/{len(annunci_da_considerare)}: {title} -> {url}")
                        
                        # Filtro per prezzo minimo, specifico per questo target
                        if price <= min_price :
                            logger.info(f"-> Annuncio scartato, prezzo ({price}) inferiore al prezzo minimo impostato ({min_price})")
                            motivazione_scarto = f"Prezzo ({annuncio['price']:.2f}€) <= Soglia Minima ({min_price:.2f}€)"
                            log_scarto("scarti_prezzo_basso.txt", link, motivazione_scarto)
                            continue

                        if price >= max_price:
                            logger.info(f"-> Annuncio scartato, prezzo ({price}) superiore al prezzo massimo impostato ({max_price})")
                            motivazione_scarto = f"Prezzo ({annuncio['price']:.2f}€) > Soglia Massima ({max_price:.2f}€)"
                            log_scarto("scarti_prezzo_alto.txt", link, motivazione_scarto)
                            continue

                        if link in annunci_gia_analizzati_set:
                            logger.info(f"-> Annuncio scartato in quanto già analizzato in passato")
                            continue

                        logger.info(f"-> Annuncio idoneo al triage, procedo.. ")

                        # --- PASSAGGIO 1: ANALISI DI TRIAGE ---
                        risultato_triage = doTriage(
                            title,
                            price,
                            img_url, 
                            triage_prompt_specifico
                        )

                        if risultato_triage['continua_analisi']:
                            logger.info(f"TRIAGE SUPERATO. Eseguo analisi approfondita...")
                            
                            # --- PASSAGGIO 2: ANALISI APPROFONDITA (SOLO SE NECESSARIO) ---
                            dettagli_annuncio = scrap_dettagli_annuncio(link)
                        
                            # LOGGING DI DEBUG PER INPUT AI
                            logger.info("="*25 + " DEBUG: INPUT PER OPENAI " + "="*25)
                            logger.info(f" - Titolo: {title}")
                            logger.info(f" - Prezzo: {price:.2f} €")
                            logger.info(f" - Descrizione: {dettagli_annuncio['description'][:200]}...") 
                            logger.info(f" - Img URL: {img_url}")
                            logger.info(f" - URL: {annuncio['url']}")
                            logger.info(f" - Vendor username: {dettagli_annuncio['vendor_username']}")
                            logger.info(f" - Vendor reviews: {dettagli_annuncio['vendor_reviews_count']}")
                            logger.info("="*75)

                            # Chiamata unificata alla funzione di analisi olistica
                            analisi_complessiva = doCompleteArticleAnalysis(
                                title, 
                                dettagli_annuncio['description'], 
                                price,
                                img_url,
                                ai_context,
                                dettagli_annuncio['vendor_username'],
                                dettagli_annuncio['vendor_reviews_count']
                            )

                            # LOGGING DI DEBUG PER OUTPUT AI
                            logger.info("*"*25 + " DEBUG: OUTPUT DA OPENAI " + "*"*25)
                            logger.info(json.dumps(analisi_complessiva, indent=2, ensure_ascii=False))
                            logger.info("*"*74)

                            # Aggiornamento della cronologia
                            annunci_gia_analizzati_set.add(link)
                            cronologia_deque.append(link)
                            salva_cronologia(cronologia_deque) # Salva subito per non perdere dati in caso di crash

                            # Logica decisionale per la notifica
                            punteggio = analisi_complessiva.get('punteggio_complessivo', 0)

                            if analisi_complessiva.get('is_interessante', False):
                                logger.info(f" ✅ Annuncio INTERESSANTE trovato! Punteggio Complessivo: {punteggio}/10.")
                                if (punteggio > 7):

                                    messaggio = (
                                        f"🔥 *Potenziale Affare Trovato!* ({expertise_name}) 🔥\n\n"
                                        f"📝 *Titolo*: {annuncio['title']}\n"
                                        f"💰 *Prezzo*: *{annuncio['price']:.2f} €*\n\n"
                                        f"🤖 *Valutazione Complessiva (Score: {punteggio}/10)*:\n"
                                        f"{analisi_complessiva.get('motivazione_complessiva', 'N/A')}\n"
                                        f"*Parole chiave*: {', '.join(analisi_complessiva.get('parole_chiave', []))}"
                                    )
                                    await invia_notifica(messaggio, link, annuncio['img_url'])
                                else:
                                    motivazione_scarto = f"Punteggio ({punteggio}/10) inferiore alla soglia. Motivazione AI: {analisi_complessiva.get('motivazione_complessiva', 'N/A')}"
                                    log_scarto("scarti_analisi_approfondita.txt", link, motivazione_scarto)
                                    logger.warning(f" ❌ Analisi approfondita ha scartato l'annuncio. {motivazione_scarto}")
                            else:
                                # --- 4. LOGGING SCARTI DALL'ANALISI APPROFONDITA ---
                                motivazione_scarto = f"Non ritenuto interessante. Motivazione AI: {analisi_complessiva.get('motivazione_complessiva', 'N/A')}"
                                log_scarto("scarti_analisi_approfondita.txt", link, motivazione_scarto)                   
                                logger.warning(f" ❌ Annuncio scartato. Punteggio Complessivo: {punteggio}/10.")

                            logger.info(f"Pausa di {INTERVALLO_INTRA_ARTICLES} secondi prima del prossimo annuncio")
                            await asyncio.sleep(INTERVALLO_INTRA_ARTICLES) 

                        else:
                            # --- 3. LOGGING SCARTI DAL TRIAGE ---
                            motivazione_triage = risultato_triage.get('motivazione', 'Nessuna motivazione fornita.')
                            log_scarto("scarti_triage.txt", link, motivazione_triage)
                            logger.warning(f" -> TRIAGE FALLITO. Annuncio scartato senza analisi approfondita.")

                    # Pausa tra un termine di ricerca e l'altro
                    logger.info(f"Pausa tattica di {INTERVALLO_INTRA_TERMS} secondi prima del prossimo termine di ricerca")

                    await asyncio.sleep(INTERVALLO_INTRA_TERMS) 
            
            logger.info("--- Scansione di tutti i target completata. In attesa del prossimo ciclo orario. ---")

        else:
            logger.info(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Pausa notturna...")

        await asyncio.sleep(INTERVALLO_INTERO_CICLO)

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        logger.warning("Shutdown richiesto dall'utente. Uscita in corso.")