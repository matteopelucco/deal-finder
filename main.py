import asyncio
import datetime  # -> Importiamo la libreria per gestire data e ora
from config import SEARCH_TERMS, MAX_HISTORY_SIZE, MAX_ANNUNCI_DA_CONSIDERARE, INTERVALLO_ORARIO
from scraper import scrap_vinted, scrap_dettagli_annuncio
from analyzer import analizza_testo_ai, analizza_immagine_ai
from notifier import invia_notifica
import os
from collections import deque  # -> Importiamo deque

# --- CONFIGURAZIONE DELLA MEMORIA PERSISTENTE ---
HISTORY_FILE = "analyzed_listings.txt"


def carica_cronologia():
    """Carica la cronologia in una deque a dimensione fissa e in un set per ricerche veloci."""
    if not os.path.exists(HISTORY_FILE):
        return set(), deque(maxlen=MAX_HISTORY_SIZE)
    
    with open(HISTORY_FILE, 'r') as f:
        # Leggiamo tutte le linee, rimuovendo spazi/a-capo
        lines = [line.strip() for line in f.readlines()]
        # Creiamo la deque solo con gli ultimi `MAX_HISTORY_SIZE` elementi
        cronologia_deque = deque(lines, maxlen=MAX_HISTORY_SIZE)
        # Il set conterrà gli stessi elementi per ricerche O(1)
        cronologia_set = set(cronologia_deque)
        return cronologia_set, cronologia_deque

def salva_cronologia(cronologia_deque: deque):
    """Salva l'intero stato della deque nel file, sovrascrivendolo."""
    with open(HISTORY_FILE, 'w') as f:
        # Scriviamo ogni elemento della deque su una nuova riga
        f.write('\n'.join(cronologia_deque))

async def main_loop():
    """Ciclo principale con memoria persistente a capienza finita e pausa notturna."""
    
    # Carichiamo la cronologia sia nel set (per velocità) sia nella deque (per ordine e dimensione)
    annunci_gia_analizzati_set, cronologia_deque = carica_cronologia()
    print(f"Caricati {len(annunci_gia_analizzati_set)} annunci dalla cronologia (capienza massima: {MAX_HISTORY_SIZE}).")

    while True:
        ora_corrente = datetime.datetime.now().hour
        
        if 0 <= ora_corrente <= 24:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Orario di attività. Inizio nuova scansione...")
            
            nuovi_annunci_analizzati = False # Flag per sapere se dobbiamo salvare

            for term in SEARCH_TERMS:
                # Aumentato a 10 per avere più chance di trovare annunci nuovi e vecchi
                risultati_scraper = scrap_vinted(term)

                annunci_da_considerare = risultati_scraper[:MAX_ANNUNCI_DA_CONSIDERARE]
                
                print(f"Termine '{term}': {len(risultati_scraper)} trovati, ne considero i primi {len(annunci_da_considerare)}.")
                for annuncio in annunci_da_considerare:

                    link = annuncio['link']

                    if link in annunci_gia_analizzati_set:
                        # print(f"Già analizzato, skippo: {annuncio['title']}") # Commentato per un log più pulito
                        continue

                    print(f"Nuovo annuncio! Analizzo: {annuncio['title']}")
                    
                    descrizione = scrap_dettagli_annuncio(link)
                    print(f"description: {descrizione}")

                    # Analizziamo con AI usando anche la descrizione
                    valutazione_testo = analizza_testo_ai(annuncio['title'], descrizione)

                    valutazione_img = analizza_immagine_ai(annuncio['img_url'])
                    
                    # Aggiungiamo il nuovo link sia al set che alla deque
                    annunci_gia_analizzati_set.add(link)
                    cronologia_deque.append(link) # Se la deque è piena, il più vecchio viene rimosso
                    nuovi_annunci_analizzati = True

                    messaggio = (
                        f"📢 *Nuovo Annuncio Trovato* (Ricerca: '{term}')\n\n"
                        f"📝 *Titolo*: {annuncio['title']}\n"
                        # Potremmo aggiungere un estratto della descrizione se non troppo lungo
                        # f"📄 *Descrizione*: {descrizione[:150]}...\n\n" 
                        f"------------------------------------\n"
                        f"🤖 *Valutazione Testo*: {valutazione_testo}\n\n"
                        f"🖼️ *Valutazione Immagine*: {valutazione_img}"
                    )
                    
                    await invia_notifica(messaggio, link, annuncio['img_url'])
                    await asyncio.sleep(10)

                await asyncio.sleep(5)
            
            # --> SALVATAGGIO EFFICIENTE
            # Salviamo su file solo se abbiamo analizzato qualcosa di nuovo in questo ciclo
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