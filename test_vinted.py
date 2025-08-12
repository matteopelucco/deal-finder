import pprint
from scraper import scrap_vinted

# Definiamo un termine di ricerca standard per il test.
# Puoi cambiarlo per testare altre parole chiave.
TEST_TERM = "monete antiche"

def test_scraping_functionality():
    """
    Esegue un test sulla funzione di scraping per verificare che
    riesca a recuperare i dati da Vinted e li stampi a console.
    """
    print(f"--- Inizio test di scraping per il termine: '{TEST_TERM}' ---")
    
    try:
        # Chiama la funzione di scraping importata dal modulo scraper.py
        annunci = scrap_vinted(TEST_TERM)
        
        # Controlla se lo scraping ha prodotto risultati
        if not annunci:
            print("\n⚠️ ATTENZIONE: Lo scraping non ha restituito alcun risultato.")
            print("Possibili cause:")
            print("1.  Nessun annuncio trovato per il termine di ricerca.")
            print("2.  Vinted potrebbe aver bloccato la richiesta (protezione anti-bot).")
            print("3.  La struttura HTML del sito di Vinted potrebbe essere cambiata, rendendo i selettori CSS obsoleti.")
            print("4.  Problema di connettività di rete.")
            return

        # Se ci sono risultati, stampa un messaggio di successo e i dettagli
        print(f"\n✅ Successo! Trovati {len(annunci)} annunci.")
        print("--- Mostro i primi 3 risultati recuperati: ---")
        
        # Usiamo pprint per stampare i dizionari in modo più leggibile
        pp = pprint.PrettyPrinter(indent=4)
        
        for i, annuncio in enumerate(annunci[:3]):
            print(f"\n--- Annuncio #{i+1} ---")
            pp.pprint(annuncio)
            
    except Exception as e:
        print(f"\n❌ ERRORE: Si è verificato un errore imprevisto durante l'esecuzione dello scraper.")
        print(f"Dettagli dell'errore: {e}")

if __name__ == "__main__":
    test_scraping_functionality()