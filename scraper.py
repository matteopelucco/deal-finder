import requests
from bs4 import BeautifulSoup
def scrap_vinted(term: str) -> list:
    """
    Effettua una ricerca su Vinted e restituisce una lista di annunci.
    Attenzione: la struttura HTML di Vinted può cambiare, richiedendo un aggiornamento
    dei selettori CSS ('div[class*="feed-grid__item"]').
    """
    print(f"Scraping per il termine: '{term}'...")
    url = f"https://www.vinted.it/catalog?search_text={term.replace(' ', '%20')}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Solleva un'eccezione per errori HTTP
    except requests.RequestException as e:
        print(f"Errore durante la richiesta a Vinted: {e}")
        return []
    soup = BeautifulSoup(response.content, "html.parser")
    results = []
    
    # Selettore CSS per gli item degli annunci (potrebbe dover essere aggiornato)
    items = soup.select('div[class*="feed-grid__item"]')
    
    for item in items:
        title_element = item.find("h2") # Cerca tag più specifici se possibile
        title = item.get_text(strip=True) # Fallback generico
        
        link_element = item.find("a")
        href = f"https://www.vinted.it{link_element.get('href')}" if link_element else None
        
        img_element = item.find("img")
        img_url = img_element['src'] if img_element and 'src' in img_element.attrs else None
        
        if href: # Aggiungi solo se c'è un link all'annuncio
            results.append({"term": term, "title": title, "link": href, "img_url": img_url})
            
    return results