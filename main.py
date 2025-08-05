import time
from config import SEARCH_TERMS, WAIT_TIME_SECONDS
from scraper import scrap_vinted
from analyzer import analizza_testo_ai, analizza_immagine_ai
from notifier import invia_notifica

def main_loop():
    """Ciclo principale dell'agente di monitoraggio."""
    annunci_gia_notificati = set()

    while True:
        print("--- Inizio nuova scansione ---")
        for term in SEARCH_TERMS:
            # Recupera gli ultimi annunci (es. i primi 3 per non essere troppo invasivo)
            annunci = scrap_vinted(term)[:3]
            
            for annuncio in annunci:
                # Controlla se l'annuncio è già stato notificato per evitare doppioni
                if annuncio['link'] in annunci_gia_notificati:
                    continue

                print(f"Analizzo: {annuncio['title']}")
                # Analisi con OpenAI
                valutazione_testo = analizza_testo_ai(annuncio['title'])
                valutazione_img = analizza_immagine_ai(annuncio['img_url'])

                # Costruisci il messaggio di notifica
                messaggio = (
                    f"📢 *Nuovo Annuncio Trovato* (Ricerca: '{term}')\n\n"
                    f"📝 *Titolo*: {annuncio['title']}\n\n"
                    f"🤖 *Valutazione Testo*: {valutazione_testo}\n\n"
                    f"🖼️ *Valutazione Immagine*: {valutazione_img}"
                )
                
                # Invia la notifica e aggiungi il link alla lista di quelli già visti
                invia_notifica(messaggio, annuncio['link'], annuncio['img_url'])
                annunci_gia_notificati.add(annuncio['link'])
                
                time.sleep(10) # Pausa tra un'analisi e l'altra per non sovraccaricare le API

            time.sleep(5) # Pausa tra una ricerca e l'altra

        print(f"--- Scansione completata. Prossima scansione tra {WAIT_TIME_SECONDS / 60} minuti. ---")
        time.sleep(WAIT_TIME_SECONDS)


if __name__ == "__main__":
    main_loop()