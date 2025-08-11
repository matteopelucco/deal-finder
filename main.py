import asyncio  # -> Importato asyncio
from config import SEARCH_TERMS, WAIT_TIME_SECONDS
from scraper import scrap_vinted
from analyzer import analizza_testo_ai, analizza_immagine_ai
from notifier import invia_notifica

async def main_loop():  # -> La funzione principale è ora async
    """Ciclo principale dell'agente di monitoraggio."""
    annunci_gia_notificati = set()

    while True:
        print("--- Inizio nuova scansione ---")
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
                
                # -> Aggiunto "await" per la chiamata asincrona
                await invia_notifica(messaggio, annuncio['link'], annuncio['img_url'])
                annunci_gia_notificati.add(annuncio['link'])
                
                # -> Usiamo asyncio.sleep() invece di time.sleep()
                await asyncio.sleep(10)

            await asyncio.sleep(5)

        print(f"--- Scansione completata. Prossima scansione tra {WAIT_TIME_SECONDS / 60} minuti. ---")
        await asyncio.sleep(WAIT_TIME_SECONDS)


if __name__ == "__main__":
    try:
        # -> Avviamo il ciclo asincrono con asyncio.run()
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\nShutdown richiesto. Uscita in corso.")