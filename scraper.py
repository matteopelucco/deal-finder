import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# -> Importiamo le costanti di configurazione
from config import VINTED_CATALOG, SCRAPER_TIMEOUT_SECONDS

# ==============================================================================
# --- CONFIGURAZIONE CENTRALE DEI SELETTORI CSS ---
# Se Vinted cambia il sito, basterà aggiornare i valori in questo dizionario.
# ==============================================================================
VINTED_SELECTORS = {
    # Selettori per la pagina dei risultati di ricerca (catalog)
    "search_results": {
        "item_card": 'div[data-testid="grid-item"]',  # Contenitore di un singolo annuncio
        "link": "a",                                 # Il tag <a> per il link
        "image": "img",                              # Il tag <img> per l'immagine
        "title": '[data-testid$="--description-title"]',  # L'elemento che contiene il titolo
        "price": '[data-testid$="--price-text"]',           # L'elemento che contiene il prezzo
    },
    # Selettori per la pagina di dettaglio di un singolo annuncio
    "item_details": {
        "description": "div[itemprop='description']"  # L'elemento che contiene la descrizione
    }
}
# ==============================================================================

def _clean_price(price_text: str) -> float:
    """Converte una stringa di prezzo (es. '3,00 €') in un numero float."""
    if not price_text:
        return 0.0
    try:
        cleaned_price = price_text.replace('€', '').replace(',', '.').strip()
        return float(cleaned_price)
    except (ValueError, TypeError):
        return 0.0

def scrap_vinted(term: str) -> list:
    """
    Effettua una ricerca su Vinted usando i selettori centralizzati.
    """
    print(f"Scraping per il termine: '{term}'...")
    base_url = "https://www.vinted.it"
    url = f"{base_url}/catalog?search_text={term.replace(' ', '%20')}&catalog[]={VINTED_CATALOG}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    try:
        response = requests.get(url, headers=headers, timeout=SCRAPER_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Errore durante la richiesta a Vinted: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    results = []

    # -> Usa il selettore centralizzato per trovare tutti gli annunci
    items = soup.select(VINTED_SELECTORS["search_results"]["item_card"])
    
    if not items:
        print(f"!!! NESSUN ANNUNCIO TROVATO. Il selettore '{VINTED_SELECTORS['search_results']['item_card']}' potrebbe essere cambiato. !!!")
        return []

    for item in items:
        # -> Usa i selettori centralizzati per trovare gli elementi interni
        link_element = item.find(VINTED_SELECTORS["search_results"]["link"], href=True)
        if not link_element:
            continue
        full_link = urljoin(base_url, link_element['href'])

        img_element = item.find(VINTED_SELECTORS["search_results"]["image"])
        img_url = img_element['src'] if img_element and 'src' in img_element.attrs else None

        title_element = item.select_one(VINTED_SELECTORS["search_results"]["title"])
        title = title_element.get_text(strip=True) if title_element else "Titolo non trovato"
        
        price_element = item.select_one(VINTED_SELECTORS["search_results"]["price"])
        price_str = price_element.get_text(strip=True) if price_element else "0,00 €"
        price_float = _clean_price(price_str)

        results.append({
            "term": term, 
            "title": title, 
            "link": full_link, 
            "price": price_float, 
            "img_url": img_url
        })

    print(f"..{len(results)} results found.")
    return results

def scrap_dettagli_annuncio(url_annuncio: str) -> str:
    """
    Visita la pagina di un singolo annuncio e ne estrae la descrizione usando i selettori centralizzati.
    """
    if not url_annuncio:
        return ""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    try:
        response = requests.get(url_annuncio, headers=headers, timeout=SCRAPER_TIMEOUT_SECONDS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # -> Usa il selettore centralizzato per la descrizione
        description_container = soup.select_one(VINTED_SELECTORS["item_details"]["description"])
        
        if description_container:
            return description_container.get_text(strip=True)
        else:
            return "Descrizione non trovata."
            
    except requests.RequestException as e:
        print(f"Errore di rete visitando {url_annuncio}: {e}")
        return "Errore durante il recupero della descrizione."
    except Exception as e:
        print(f"Errore imprevisto durante lo scraping dei dettagli: {e}")
        return "Errore imprevisto."