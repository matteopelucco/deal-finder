import asyncio
import datetime  # -> Importiamo la libreria per gestire data e ora
from config import SEARCH_TERMS, WAIT_TIME_SECONDS
from scraper import scrap_vinted
from analyzer import analizza_testo_ai, analizza_immagine_ai
from notifier import invia_notifica

async def main_loop():
    """Ciclo principale dell'agente di monitoraggio con pausa notturna."""
    annunci_gia_notificati = set()

    # Impostiamo l'intervallo di attesa a 1 ora (3600 secondi)
    # Lo definiamo qui per chiarezza
    INTERVALLO_ORARIO = 3600 

    while True:
        # --> CONTROLLO ORARIO: Il cuore della nuova logica
        ora_corrente = datetime.datetime.now().hour
        
        # Le ore di attività vanno dalle 7:00 alle 23:00 (incluse)
        if 7 <= ora_corrente <= 23:
            
            # --- BLOCCO DI LOGICA ATTIVA ---
            # Se siamo nell'orario giusto, eseguiamo tutto come prima
            
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Orario di attività. Inizio nuova scansione...")
            
            for term in SEARCH_TERMS:
                annunci = scrap_vinted(term)[:3]
                
                for annuncio in annunci:
                    if annuncio['link'] in annunci_gia_notificati:
                        continue

                    print(f"Analizzo: {annuncio['title']}")
                    valutazione_testo = analizza_testo_ai(annuncio['title'])
                    valutazione_img = analizza_immagine_ai(annuncio['img_url'])

                    messaggio = (
                        f"📢 *Nuovo Annuncio Trovato* (Ricerca: '{term}')\n\n"
                        f"📝 *Titolo*: {annuncio['title']}\n\n"
                        f"🤖 *Valutazione Testo*: {valutazione_testo}\n\n"
                        f"🖼️ *Valutazione Immagine*: {valutazione_img}"
                    )
                    
                    await invia_notifica(messaggio, annuncio['link'], annuncio['img_url'])
                    annunci_gia_notificati.add(annuncio['link'])
                    await asyncio.sleep(10)

                await asyncio.sleep(5)
            
            print("--- Scansione completata. ---")

        else:
            # --- BLOCCO DI PAUSA NOTTURNA ---
            # Se è notte, non facciamo nulla e lo comunichiamo nel log
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Pausa notturna. Prossimo controllo tra un'ora.")

        # Pausa di un'ora prima del prossimo controllo
        await asyncio.sleep(INTERVALLO_ORARIO)


if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\nShutdown richiesto. Uscita in corso.")