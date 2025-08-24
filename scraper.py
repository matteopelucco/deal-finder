import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re 

# Import delle costanti di configurazione necessarie
from config import SCRAPER_TIMEOUT_SECONDS

# ==============================================================================
# --- CONFIGURAZIONE CENTRALE DEI SELETTORI CSS ---
# Se Vinted cambia la struttura del suo sito, basterà aggiornare i valori
# in questo dizionario per far funzionare di nuovo lo scraper.
# ==============================================================================
VINTED_SELECTORS = {
    # Selettori per la pagina dei risultati di ricerca (catalogo)
    "search_results": {
        "item_card": 'div[data-testid="grid-item"]',
        "link": "a",
        "image": "img",
        "title": '[data-testid$="--description-title"]',
        "price": '[data-testid$="--price-text"]',
    },
    # Selettori per la pagina di dettaglio di un singolo annuncio
    "item_details": {
        # Selettore per il blocco che contiene la descrizione testuale dell'annuncio
        "description": "div[itemprop='description']",
        "vendor_username": '[data-testid="profile-username"]',
        "vendor_reviews_text": 'div.web_ui__Rating__label > span.web_ui__Text__text'
    }
}
# ==============================================================================

def _clean_price(price_text: str) -> float:
    """
    Pulisce una stringa di prezzo (es. '125,00 €') e la converte in un numero float.
    Gestisce la valuta, gli spazi e la virgola come separatore decimale.
    """
    if not price_text:
        return 0.0
    try:
        # Rimuove il simbolo dell'euro, gli spazi, sostituisce la virgola e converte
        cleaned_price = price_text.replace('€', '').replace(',', '.').strip()
        return float(cleaned_price)
    except (ValueError, TypeError):
        # In caso di errore di conversione, restituisce 0.0 per evitare crash
        return 0.0

def scrap_vinted(term: str, vinted_catalog_id: int) -> list:
    """
    Esegue una ricerca su Vinted per un dato termine e ID catalogo,
    usando i selettori centralizzati per estrarre i dati degli annunci.
    Restituisce una lista di dizionari, ognuno rappresentante un annuncio.
    """
    base_url = "https://www.vinted.it"
    # L'URL viene costruito dinamicamente con il termine e l'ID catalogo forniti
    url = f"{base_url}/catalog?search_text={term.replace(' ', '%20')}&catalog[]={vinted_catalog_id}"
    # Headers per simulare un browser e ridurre la probabilità di essere bloccati
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    try:
        response = requests.get(url, headers=headers, timeout=SCRAPER_TIMEOUT_SECONDS)
        response.raise_for_status()  # Solleva un'eccezione per errori HTTP (es. 403, 404, 500)
    except requests.RequestException as e:
        print(f"ERRORE durante la richiesta a Vinted per '{term}': {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    results = []

    # Usa il selettore centralizzato per trovare tutti i contenitori degli annunci
    items = soup.select(VINTED_SELECTORS["search_results"]["item_card"])
    
    if not items:
        print(f"     INFO: Nessun annuncio trovato per '{term}'. Il selettore '{VINTED_SELECTORS['search_results']['item_card']}' potrebbe essere obsoleto o non ci sono risultati.")
        return []

    for item in items:
        # Per ogni annuncio, estrae i singoli dati usando i selettori relativi
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
            "img_url": img_url,
            "url": full_link
        })

    return results

def scrap_dettagli_annuncio(url_annuncio: str) -> str:
    """
    Visita la pagina di un singolo annuncio e ne estrae la descrizione testuale.
    """

    default_details = {
        "description": "Descrizione non trovata.",
        "vendor_username": "Sconosciuto",
        "vendor_reviews_count": 0
    }

    if not url_annuncio:
        return default_details
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    try:
        response = requests.get(url_annuncio, headers=headers, timeout=SCRAPER_TIMEOUT_SECONDS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Estrazione descrizione
        description_container = soup.select_one(VINTED_SELECTORS["item_details"]["description"])
        if description_container:
            description = description_container.get_text(strip=True, separator='\n')
        else:
            description = "Descrizione non trovata."
        
        # Estrazione username venditore
        username_element = soup.select_one(VINTED_SELECTORS["item_details"]["vendor_username"])
        if username_element:
            vendor_username = username_element.get_text(strip=True) if username_element else "Sconosciuto"
        else:
            vendor_username = "Venditore non trovato"
        
        # Estrazione e pulizia numero recensioni
        reviews_count = 0
        reviews_element = soup.select_one(VINTED_SELECTORS["item_details"]["vendor_reviews_text"])
        if reviews_element:
            # Usiamo un'espressione regolare per estrarre solo i numeri dal testo (es. "54 recensioni")
            numbers = re.findall(r'\d+', reviews_element.get_text())
            if numbers:
                reviews_count = int(numbers[0])
        return {
            "description": description,
            "vendor_username": vendor_username,
            "vendor_reviews_count": reviews_count
        }
    
    except Exception as e:
        print(f"        ERRORE imprevisto durante lo scraping dei dettagli: {e}")
        return default_details