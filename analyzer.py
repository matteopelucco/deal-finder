import json
from openai import OpenAI
from config import OPENAI_KEY, TRIAGE_AI_PROMPT, DEBUG_TRIAGE

# Crea un'istanza del client OpenAI che verrà riutilizzata per tutte le chiamate
client = OpenAI(api_key=OPENAI_KEY)
MODELO_ANALISI = "gpt-5-mini"

# ==============================================================================
# --- NUOVA FUNZIONE DI TRIAGE ---
# ==============================================================================
def analizza_triage(titolo: str, prezzo: float, img_url: str) -> bool:
    """
    Esegue un'analisi preliminare robusta. Se DEBUG_TRIAGE è True, stampa
    la motivazione dell'AI. Restituisce True se l'annuncio merita
    un'analisi approfondita, altrimenti False.
    """
    


    prompt_text = f"""
    {TRIAGE_AI_PROMPT}

    --- DATI DA VALUTARE ---
    - Titolo: "{titolo}"
    - Prezzo: "{prezzo:.2f} €"
    """


    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text}
            ]
        }
    ]

    if img_url:
        messages[0]["content"].append({"type": "image_url", "image_url": {"url": img_url}})
    

    try:
        response = client.chat.completions.create(
            model=MODELO_ANALISI,
            response_format={"type": "json_object"},
            messages=messages,
            max_completion_tokens=500
        )
        
        # --- Blocco di controllo robusto (invariato) ---
        if not response or not response.choices or response.choices[0].finish_reason != 'stop':
            print("        ERRORE TRIAGE: Risposta API vuota o interrotta.")
            return False
        message_content = response.choices[0].message.content
        if not message_content:
            print("        ERRORE TRIAGE: Contenuto del messaggio vuoto.")
            return False
            
        json_response = json.loads(message_content)
        
        # Estraiamo entrambi i valori dal JSON
        continua_analisi = json_response.get("continua_analisi", False)
        motivazione = json_response.get("motivazione", "Nessuna motivazione fornita.")
        # --- NUOVA LOGICA DI DEBUG ---
        # Se la modalità di debug è attiva, stampiamo la motivazione
        if DEBUG_TRIAGE:
            # Se l'analisi viene scartata, stampiamo il motivo per capire perché
            if not continua_analisi:
                print(f"           -> TRIAGE FALLITO. Motivo AI: '{motivazione}'")
            else:
                # Possiamo anche loggare il motivo del successo, se vogliamo
                print(f"           -> TRIAGE SUPERATO. Motivo AI: '{motivazione}'")
        
        # La funzione restituisce comunque solo il booleano, per non alterare il flusso di main.py
        return continua_analisi
    except Exception as e:
        print(f"        ERRORE durante l'analisi di triage: {e}")
        return False


def _get_default_response() -> dict:
    """
    Restituisce una risposta di default strutturata come un JSON non interessante.
    Questa funzione viene chiamata in caso di qualsiasi errore per garantire che
    il programma principale non si blocchi e possa continuare l'esecuzione.
    """
    return {
        "is_interessante": False,
        "punteggio_complessivo": 0,
        "motivazione_complessiva": "Analisi AI fallita o non conclusiva.",
        "parole_chiave": []
    }

def analizza_annuncio_completo(titolo: str, descrizione: str, prezzo: float, img_url: str, 
                               ai_context_prompt: str, 
                               vendor_username: str, vendor_reviews_count: int) -> dict:
    """
    Esegue un'analisi olistica e generica di un annuncio (testo, prezzo, immagine)
    basandosi su un contesto di expertise fornito (ai_context_prompt) in una singola chiamata API.
    Restituisce un dizionario JSON con la valutazione complessiva.
    """
    # Il prompt principale che definisce la struttura della risposta attesa dall'AI.
    # Riceve il contesto specifico per la categoria tramite il parametro 'ai_context_prompt'.
    prompt = f"""
    {ai_context_prompt}

    

    Analizza i seguenti dati dell'annuncio e del venditore basandoti ESCLUSIVAMENTE sulle regole e i criteri forniti sopra.
    La tua risposta deve essere in formato JSON con la struttura:
    {{
      "is_interessante": boolean,
      "punteggio_complessivo": integer (1-10),
      "motivazione_complessiva": "stringa di testo (massimo 80 parole)",
      "parole_chiave": ["lista", "di", "stringhe"]
    }}

    --- DATI DELL'ANNUNCIO DA ANALIZZARE ---
    - Titolo: "{titolo}"
    - Descrizione: "{descrizione}"
    - Prezzo: "{prezzo:.2f} €"
    
    --- DATI CONTESTUALI SUL VENDITORE ---
    - Username: "{vendor_username}"
    - Numero di Recensioni: {vendor_reviews_count}

    """
    
    # Costruisce il payload del messaggio per l'API, includendo sia testo che immagine.
    messages = [
        {
            "role": "system",
            "content": "Sei un esperto critico e selettivo che analizza annunci completi e risponde solo con oggetti JSON validi."
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt}
            ]
        }
    ]
    
    # Aggiunge l'URL dell'immagine al payload solo se è stato fornito,
    # per evitare di inviare un URL vuoto all'API.
    if img_url:
        messages[1]["content"].append({"type": "image_url", "image_url": {"url": img_url}})
    else:
        # Se non c'è immagine, è bene informare esplicitamente l'AI.
        messages[1]["content"][0]["text"] += "\n- Immagine: Non fornita."


    try:
        response = client.chat.completions.create(
            model=MODELO_ANALISI,
            # Forza l'API a restituire una stringa in formato JSON, riducendo gli errori di parsing.
            response_format={"type": "json_object"},
            messages=messages,
            # Limite di token per la risposta, per evitare risposte troppo lunghe e costi imprevisti.
            max_completion_tokens=2000
        )
        
        # Log di debug per monitorare i costi e l'utilizzo dei token.
        print(f"        DEBUG USO COMBINATO: Prompt={response.usage.prompt_tokens}, Completion={response.usage.completion_tokens}")
        
        # Parsing della stringa JSON per convertirla in un dizionario Python.
        json_response = json.loads(response.choices[0].message.content)
        return json_response

    except Exception as e:
        # Cattura qualsiasi errore (di rete, API, parsing, etc.)
        # e restituisce una risposta di default per non bloccare il bot.
        print(f"        ERRORE durante l'analisi AI olistica: {e}")
        return _get_default_response()