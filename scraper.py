import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin  # -> Importato urljoin per la gestione sicura degli URL

from config import VINTED_CATALOG, SCRAPER_TIMEOUT_SECONDS

def scrap_vinted(term: str) -> list:
    """
    Effettua una ricerca su Vinted in una categoria specifica e restituisce una lista di annunci.
    """
    print(f"Scraping per il termine: '{term}'...")
    
    base_url = "https://www.vinted.it"
    # Costruisce l'URL di ricerca con il termine e la categoria specificata in config.py
    url = f"{base_url}/catalog?search_text={term.replace(' ', '%20')}&catalog[]={VINTED_CATALOG}"
    
    print(f"URL: {url}")

    # Aggiunti headers per simulare un browser reale e prevenire blocchi
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    try:
        response = requests.get(url, headers=headers, timeout=SCRAPER_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Errore durante la richiesta a Vinted: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    results = []
    
    # Selettore CSS per gli item degli annunci (mantenuto il tuo selettore robusto)
    items = soup.select('div[class*="feed-grid__item"]')

    for item in items:
        # Estrazione più precisa del titolo e del link
        container_element = item.select_one("div.new-item-box__container")
        if not container_element:
            continue
            
        link_element = container_element.find("a", href=True)
        if not link_element:
            continue

        # --> APPLICAZIONE DELLA CORREZIONE CON URLJOIN <--
        # Questo costruisce l'URL completo in modo sicuro, evitando duplicati.
        full_link = urljoin(base_url, link_element['href'])

        # Estrazione più precisa del titolo (se disponibile)
        # title_element = container_element.select_one('[data-testid="item-box-title"]')
        title_element = container_element.select_one('.new-item-box__description p')
        title = title_element.get_text(strip=True) if title_element else "Titolo non trovato"

        img_element = item.find("img")
        img_url = img_element['src'] if img_element and 'src' in img_element.attrs else None

        if full_link:
            results.append({"term": term, "title": title, "link": full_link, "img_url": img_url})

    print(f"..{len(results)} results found.")
    return results


def scrap_dettagli_annuncio(url_annuncio: str) -> str:
    """
    Visita la pagina di un singolo annuncio e ne estrae la descrizione testuale.
    """
    if not url_annuncio:
        return ""

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    print(f"url annuncio: {url_annuncio}")

    try:
        response = requests.get(url_annuncio, headers=headers, timeout=SCRAPER_TIMEOUT_SECONDS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # --> SELETTORE CORRETTO BASATO SULL'HTML FORNITO <--
        description_container = soup.select_one("div[itemprop='description']")
        if description_container:
            # Usiamo .get_text() per estrarre tutto il testo contenuto,
            # anche se è annidato in altri span o div.
            return description_container.get_text(strip=True)
        else:
            return "Descrizione non trovata."

    except requests.RequestException as e:
        print(f"Errore di rete visitando {url_annuncio}: {e}")
        return "Errore durante il recupero della descrizione."
    except Exception as e:
        print(f"Errore imprevisto durante lo scraping dei dettagli: {e}")
        return "Errore imprevisto."