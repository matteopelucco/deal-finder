import asyncio
import datetime
import os
from collections import deque
import json

from config import SEARCH_TERMS, MAX_HISTORY_SIZE, MAX_ANNUNCI_DA_CONSIDERARE, INTERVALLO_ORARIO, INTERVALLO_INTRA_TERMS, INTERVALLO_INTRA_ARTICLES
from scraper import scrap_vinted, scrap_dettagli_annuncio
from analyzer import analizza_testo_ai, analizza_immagine_ai
from notifier import invia_notifica

# --- (Le funzioni di gestione della cronologia rimangono invariate) ---
HISTORY_FILE = "analyzed_listings.txt"

def carica_cronologia():
    if not os.path.exists(HISTORY_FILE):
        return set(), deque(maxlen=MAX_HISTORY_SIZE)
    with open(HISTORY_FILE, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
        cronologia_deque = deque(lines, maxlen=MAX_HISTORY_SIZE)
        cronologia_set = set(cronologia_deque)
        return cronologia_set, cronologia_deque

def salva_cronologia(cronologia_deque: deque):
    with open(HISTORY_FILE, 'w') as f:
        f.write('\n'.join(cronologia_deque))

async def main_loop():
    """Ciclo principale con filtro intelligente delle notifiche."""
    
    annunci_gia_analizzati_set, cronologia_deque = carica_cronologia()
    print(f"Caricati {len(annunci_gia_analizzati_set)} annunci dalla cronologia (capienza massima: {MAX_HISTORY_SIZE}).")

    while True:
        ora_corrente = datetime.datetime.now().hour
        
        # Corretta la logica per la pausa notturna (attivo dalle 7:00 alle 23:00)
        if 7 <= ora_corrente <= 23:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Orario di attività. Inizio nuova scansione...")
            
            nuovi_annunci_analizzati = False

            for i, term in enumerate(SEARCH_TERMS):

                # Attendiamo qualche attimo tra una ricerca e la seguente, per essere gentili con le API.
                if i > 0:
                    print(f"Pausa di {INTERVALLO_INTRA_TERMS} secondi prima del prossimo termine di ricerca...")
                    await asyncio.sleep(INTERVALLO_INTRA_TERMS)

                risultati_scraper = scrap_vinted(term)
                annunci_da_considerare = risultati_scraper[:MAX_ANNUNCI_DA_CONSIDERARE]
                print(f"Termine '{term}': {len(risultati_scraper)} trovati, ne considero i primi {len(annunci_da_considerare)}.")

                for annuncio in annunci_da_considerare:
                    link = annuncio['link']
                    if link in annunci_gia_analizzati_set:
                        continue

                    print(f"Nuovo annuncio! Analizzo: {annuncio['title']}")
                    descrizione = scrap_dettagli_annuncio(link)
                    
                    # ==============================================================================
                    # --- BLOCCO DI LOGGING (INPUT AI) ---
                    # ==============================================================================
                    print("\n" + "="*25 + " DEBUG: INPUT PER OPENAI " + "="*25)
                    print(f"  - Titolo: {annuncio['title']}")
                    print(f"  - Prezzo: {annuncio['price']:.2f} €")
                    # Tronchiamo la descrizione nel log per non inondare il terminale
                    print(f"  - Descrizione: {descrizione[:200]}...") 
                    print(f"  - Img URL: {annuncio['img_url']}")
                    print("="*75)
                    # ==============================================================================
                    

                    analisi_testo = analizza_testo_ai(
                        annuncio['title'], 
                        descrizione, 
                        annuncio['price']
                    )

                    analisi_immagine = analizza_immagine_ai(annuncio['img_url'])
                   
                    # ==============================================================================
                    # --- BLOCCO DI LOGGING (OUTPUT AI) ---
                    # ==============================================================================
                    print("\n" + "*"*25 + " DEBUG: OUTPUT DA OPENAI " + "*"*25)
                    print("--- Analisi Testo (JSON):")
                    # Usiamo json.dumps per stampare il dizionario in modo formattato e leggibile
                    print(json.dumps(analisi_testo, indent=2, ensure_ascii=False))
                    print("\n--- Analisi Immagine (JSON):")
                    print(json.dumps(analisi_immagine, indent=2, ensure_ascii=False))
                    print("*"*74 + "\n")
                    # ==============================================================================

                    # L'annuncio viene registrato come analizzato, a prescindere dal risultato
                    annunci_gia_analizzati_set.add(link)
                    cronologia_deque.append(link)
                    nuovi_annunci_analizzati = True

                    # --- LOGICA DECISIONALE PER LE NOTIFICHE ---
                    # Inviamo una notifica solo se ALMENO UNA delle due analisi è interessante
                    if analisi_testo.get('is_interessante', False) or analisi_immagine.get('is_interessante', False):
                        print(f"✅ Annuncio INTERESSANTE trovato!...")
                        # -> AGGIORNATO IL MESSAGGIO per includere il prezzo
                        messaggio = (
                            f"🔥 *Potenziale Affare Trovato!* 🔥 (Ricerca: '{term}')\n\n"
                            f"📝 *Titolo*: {annuncio['title']}\n"
                            f"💰 *Prezzo*: *{annuncio['price']:.2f} €*\n\n" # Aggiunto il prezzo
                            f"🤖 *Valutazione Testo (Score: {analisi_testo.get('punteggio', 0)}/10)*:\n"
                            f"{analisi_testo.get('motivazione', 'N/A')}\n"
                            f"*Parole chiave*: {', '.join(analisi_testo.get('parole_chiave', []))}\n\n"
                            f"🖼️ *Valutazione Immagine (Score: {analisi_immagine.get('punteggio', 0)}/10)*:\n"
                            f"{analisi_immagine.get('motivazione', 'N/A')}\n"
                            f"*Parole chiave*: {', '.join(analisi_immagine.get('parole_chiave', []))}"
                        )
                        
                        await invia_notifica(messaggio, link, annuncio['img_url'])
                    
                    else:
                        # Se l'annuncio non è interessante, lo registriamo solo nel log
                        print(f"❌ Annuncio scartato. Punteggi (T/I): {analisi_testo.get('punteggio', 0)}/{analisi_immagine.get('punteggio', 0)}.")

                    # Pausa tra un'analisi e l'altra per essere più gentili con le API
                    await asyncio.sleep(INTERVALLO_INTRA_ARTICLES) 

                await asyncio.sleep(5)
            
            if nuovi_annunci_analizzati:
                salva_cronologia(cronologia_deque)
                print("--- Scansione completata. Cronologia aggiornata su file. ---")
            else:
                print("--- Scansione completata. Nessun nuovo annuncio trovato. ---")
        else:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Pausa notturna...")

        await asyncio.sleep(INTERVALLO_ORARIO)

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\nShutdown richiesto. Uscita in corso.")