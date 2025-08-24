import asyncio
import datetime
import os
from collections import deque
import json

# Import delle configurazioni e delle funzioni dai nostri moduli
from config import SEARCH_TARGETS, MAX_HISTORY_SIZE, MAX_ANNUNCI_DA_CONSIDERARE, INTERVALLO_ORARIO, INTERVALLO_INTRA_ARTICLES, INTERVALLO_INTRA_TERMS
from scraper import scrap_vinted, scrap_dettagli_annuncio
from analyzer import analizza_annuncio_completo
from notifier import invia_notifica

# --- GESTIONE DELLA CRONOLOGIA PERSISTENTE ---

HISTORY_FILE = "analyzed_listings.txt"

def carica_cronologia():
    """
    Carica la cronologia degli annunci già analizzati da un file di testo.
    Usa un set per ricerche veloci O(1) e una deque a dimensione fissa per gestire il limite.
    """
    if not os.path.exists(HISTORY_FILE):
        return set(), deque(maxlen=MAX_HISTORY_SIZE)
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            cronologia_deque = deque(lines, maxlen=MAX_HISTORY_SIZE)
            cronologia_set = set(cronologia_deque)
            return cronologia_set, cronologia_deque
    except Exception as e:
        print(f"ERRORE nel caricamento della cronologia: {e}. Ripartenza con cronologia vuota.")
        return set(), deque(maxlen=MAX_HISTORY_SIZE)

def salva_cronologia(cronologia_deque: deque):
    """Salva l'intero stato della deque nel file, sovrascrivendolo."""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cronologia_deque))
    except Exception as e:
        print(f"ERRORE nel salvataggio della cronologia: {e}")


async def main_loop():
    """
    Ciclo principale del bot. Gestisce i target di expertise, esegue le ricerche,
    filtra i risultati, orchestra l'analisi AI e invia le notifiche.
    """
    annunci_gia_analizzati_set, cronologia_deque = carica_cronologia()
    print(f"Caricati {len(annunci_gia_analizzati_set)} annunci dalla cronologia (capienza massima: {MAX_HISTORY_SIZE}).")

    while True:
        ora_corrente = datetime.datetime.now().hour
        
        # Il bot è attivo solo in questa finestra oraria
        if 7 <= ora_corrente <= 25:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Orario di attività. Inizio nuova scansione...")
            
            # --- CICLO ESTERNO SUI CAMPI DI EXPERTISE ---
            for target in SEARCH_TARGETS:
                expertise_name = target["expertise_name"]
                catalog_id = target["vinted_catalog_id"]
                min_price = target["min_price_to_consider"]
                max_price = target["max_price_to_consider"]
                ai_context = target["ai_context_prompt"]
                search_terms = target["search_terms"]

                print(f"\n--- Inizio Scansione Expertise: '{expertise_name}' ---")

                # --- CICLO INTERNO SUI TERMINI DI RICERCA DI QUESTA EXPERTISE ---
                for term in search_terms:
                    print(f"  -> Ricerca per il termine: '{term}' (Catalogo: {catalog_id})")
                    
                    risultati_scraper = scrap_vinted(term, catalog_id)
                    annunci_da_considerare = risultati_scraper[:MAX_ANNUNCI_DA_CONSIDERARE]
                    print(f"     Trovati {len(risultati_scraper)} annunci, ne considero i primi {len(annunci_da_considerare)}.")

                    for annuncio in annunci_da_considerare:
                        # Filtro per prezzo minimo, specifico per questo target
                        if annuncio['price'] <= min_price :
                            continue
                        if annuncio['price'] >= max_price:
                            continue

                        # Filtro per annunci già analizzati in passato
                        link = annuncio['link']
                        if link in annunci_gia_analizzati_set:
                            continue

                        print(f"        -> Nuovo annuncio! Analizzo: {annuncio['title']}")
                        descrizione = scrap_dettagli_annuncio(link)
                        
                        # LOGGING DI DEBUG PER INPUT AI
                        print("\n" + "="*25 + " DEBUG: INPUT PER OPENAI " + "="*25)
                        print(f"          - Titolo: {annuncio['title']}")
                        print(f"          - Prezzo: {annuncio['price']:.2f} €")
                        print(f"          - Descrizione: {descrizione[:200]}...") 
                        print(f"          - Img URL: {annuncio['img_url']}")
                        print(f"          - URL: {annuncio['url']}")
                        print("="*75)

                        # Chiamata unificata alla funzione di analisi olistica
                        analisi_complessiva = analizza_annuncio_completo(
                            annuncio['title'], 
                            descrizione, 
                            annuncio['price'],
                            annuncio['img_url'],
                            ai_context
                        )

                        # LOGGING DI DEBUG PER OUTPUT AI
                        print("\n" + "*"*25 + " DEBUG: OUTPUT DA OPENAI " + "*"*25)
                        print(json.dumps(analisi_complessiva, indent=2, ensure_ascii=False))
                        print("*"*74 + "\n")

                        # Aggiornamento della cronologia
                        annunci_gia_analizzati_set.add(link)
                        cronologia_deque.append(link)
                        salva_cronologia(cronologia_deque) # Salva subito per non perdere dati in caso di crash

                        # Logica decisionale per la notifica
                        if analisi_complessiva.get('is_interessante', False):
                            punteggio = analisi_complessiva.get('punteggio_complessivo', 0)
                            print(f"        ✅ Annuncio INTERESSANTE trovato! Punteggio Complessivo: {punteggio}/10. Invio notifica...")

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
                            punteggio = analisi_complessiva.get('punteggio_complessivo', 0)
                            print(f"        ❌ Annuncio scartato. Punteggio Complessivo: {punteggio}/10.")

                        print(f"Pausa tattica di {INTERVALLO_INTRA_ARTICLES} secondi prima del prossimo annuncio")
                        await asyncio.sleep(INTERVALLO_INTRA_ARTICLES) # Pausa tra l'analisi di annunci singoli

                    # Pausa tra un termine di ricerca e l'altro
                    print(f"Pausa tattica di {INTERVALLO_INTRA_TERMS} secondi prima del prossimo termine di ricerca")

                    await asyncio.sleep(INTERVALLO_INTRA_TERMS) 
            
            print("\n--- Scansione di tutti i target completata. In attesa del prossimo ciclo orario. ---")

        else:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Pausa notturna...")

        await asyncio.sleep(INTERVALLO_ORARIO)

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\nShutdown richiesto dall'utente. Uscita in corso.")