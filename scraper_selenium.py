import requests, os, datetime, time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re 



# Importazioni per Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# --- CONFIGURAZIONE SELENIUM ---
# Inserisci qui il percorso dove hai salvato chromedriver.exe
CHROME_DRIVER_PATH = r'C:\dev\software\selenium\chromedriver-win64\chromedriver.exe'

# Import delle costanti di configurazione necessarie
from config import SCRAPER_TIMEOUT_SECONDS, DEBUG_SCRAPER_HTML

# ==============================================================================
# --- CONFIGURAZIONE CENTRALE DEI SELETTORI CSS ---
# Se Vinted cambia la struttura del suo sito, basterà aggiornare i valori
# in questo dizionario per far funzionare di nuovo lo scraper.
# ==============================================================================
VINTED_SELECTORS = {
    # Selettori per la pagina dei risultati di ricerca (catalogo)
    "search_results": {
        "item_card": 'div[data-testid="grid-item"]',
        "link": 'a[data-testid$="--overlay-link"]',
        "image": 'img[data-testid$="--image--img"]',
        "title": 'p[data-testid$="--description-title"]',
        "price": 'p[data-testid$="--price-text"]',
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


    # Impostazioni di Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Esegui senza aprire una finestra del browser
    options.add_argument("--log-level=3") # Riduci il logging nel terminale
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    # options.add_argument("--start-maximized")
    
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    
    print(f"DEBUG: Scraping URL -> ", url)

    try:
        driver.get(url)
        
        # FASE 1: Gestione Cookie
        try:
            cookie_button_locator = (By.ID, "onetrust-accept-btn-handler")
            cookie_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(cookie_button_locator))
            cookie_button.click()
            WebDriverWait(driver, 5).until(EC.invisibility_of_element_located(cookie_button_locator))
        except (TimeoutException, NoSuchElementException):
            print("        INFO: Nessun banner dei cookie gestito.")
        # FASE 2: Scroll e Attesa Risultati
        driver.execute_script("window.scrollTo(0, 500);")
        WebDriverWait(driver, SCRAPER_TIMEOUT_SECONDS).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, VINTED_SELECTORS["search_results"]["item_card"]))
        )
        print(f"    INFO: Griglia dei prodotti trovata per '{term}'. Eseguo il parsing...")
        # --- CORREZIONE CHIAVE: PARSING IMMEDIATO ---
        page_html = driver.page_source

        # --- NUOVA LOGICA DI DEBUG HTML ---
        if DEBUG_SCRAPER_HTML:
            # Crea la cartella di debug se non esiste
            debug_dir = "debug_logs"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            
            # Crea un nome di file unico con il termine di ricerca e un timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_term = re.sub(r'[\\/*?:"<>|]', "", term) # Rimuove caratteri illegali dal nome del file
            file_path = os.path.join(debug_dir, f"debug_scraper_{safe_term}_{timestamp}.html")
            
            try:
                # Salva il contenuto HTML grezzo nel file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(page_html)
                print(f"DEBUG: HTML della ricerca salvato in '{file_path}'")
            except Exception as e:
                print(f"ERROR: Impossibile salvare il file HTML di debug: {e}")
        # --- FINE LOGICA DI DEBUG ---  

        # Parsing con BeautifulSoup
        soup = BeautifulSoup(page_html, 'lxml') # Usiamo il parser lxml che abbiamo confermato funzionare
        item_cards = soup.select(VINTED_SELECTORS["search_results"]["item_card"])
        
        print(f"DEBUG: found {len(item_cards)} cards")

        if not item_cards:
            # Questo messaggio ora indica un vero problema di parsing, non di caricamento
            print(f"ATTENZIONE: Nessun 'item_card' trovato da BeautifulSoup per '{term}' nonostante la griglia fosse presente.")
            driver.quit()
            return []
        
        # Estrazione dei dati
        results = []

        for item in item_cards:

            link_element = item.select_one (VINTED_SELECTORS["search_results"]["link"], href=True)
            if not link_element:
                print(f"ERROR: link non trovato")
                continue
            full_link = urljoin(base_url, link_element['href'])

            img_element = item.select_one (VINTED_SELECTORS["search_results"]["image"])
            img_url = img_element['src'] if img_element and 'src' in img_element.attrs else None

            title_element = item.select_one(VINTED_SELECTORS["search_results"]["title"])
            title = title_element.get_text(strip=True) if title_element else "Titolo non trovato"
            
            price_element = item.select_one(VINTED_SELECTORS["search_results"]["price"])
            price_str = price_element.get_text(strip=True) if price_element else "0,00 €"
            price_float = _clean_price(price_str)

            results.append({
                "term": term,
                "link": full_link,
                "price": price_float,
                "img_url": img_url,
                "url": full_link,
                "title": title
            })

        driver.quit()
        return results
    except Exception as e:
        print(f"ERRORE: Errore grave nel processo di scraping per '{term}'. Errore: {e}")
        driver.quit()
        return []

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