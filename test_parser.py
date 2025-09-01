from bs4 import BeautifulSoup

# Inserisci qui il nome del file HTML che hai salvato
HTML_FILE = 'debug_logs/debug_scraper_lotto monete_20250902_001251.html'

# I selettori che stiamo testando
ITEM_CARD_SELECTOR = 'div[data-testid="grid-item"]'
# Aggiungi qui anche i selettori interni se vuoi testarli
TITLE_SELECTOR = 'p[data-testid$="--description-title"]'

try:
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Usiamo il parser lxml, che è molto robusto.
    # Se non lo hai, installalo con: pip install lxml
    soup = BeautifulSoup(html_content, 'lxml')

    cards = soup.select(ITEM_CARD_SELECTOR)

    print(f"--- TEST DI PARSING SUL FILE: {HTML_FILE} ---")
    print(f"Parser utilizzato: lxml")
    print(f"Selettore per le card: '{ITEM_CARD_SELECTOR}'")
    print(f"Numero di card trovate: {len(cards)}")
    print("-------------------------------------------------")

    if cards:
        print("\nAnalisi della prima card trovata:")
        first_card = cards[0]
        
        title_element = first_card.select_one(TITLE_SELECTOR)
        if title_element:
            print(f"  - Titolo trovato: '{title_element.get_text(strip=True)}'")
        else:
            print(f"  - ERRORE: Titolo non trovato nella prima card con il selettore '{TITLE_SELECTOR}'")
        
        # Stampa una parte dell'HTML della prima card per l'analisi manuale
        print("\nHTML della prima card (primi 300 caratteri):")
        print(str(first_card)[:300] + "...")

except FileNotFoundError:
    print(f"ERRORE: File '{HTML_FILE}' non trovato. Assicurati che il nome e il percorso siano corretti.")
except Exception as e:
    print(f"Si è verificato un errore: {e}")