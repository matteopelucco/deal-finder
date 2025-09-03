import json
from openai import OpenAI
from config import OPENAI_KEY, TRIAGE_AI_PROMPT

# Crea un'istanza del client OpenAI che verrà riutilizzata per tutte le chiamate
client = OpenAI(api_key=OPENAI_KEY)
AI_MODEL = "gpt-5-mini"
TRIAGE_TOKENS = 800
COMPLETE_ANALYSIS_TOKENS = 2000

# ------------------------------------------------
# Esegue un'analisi preliminare basasndosi solamente su pochi dati recuperati dalla lista degli elementi
# Serve prevalementemente per ottimizzare i costi e i tempi OpenAI
# ------------------------------------------------
def doTriage(titolo: str, prezzo: float, img_url: str) -> dict:

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
            model=AI_MODEL,
            response_format={"type": "json_object"},
            messages=messages,
            max_completion_tokens=TRIAGE_TOKENS
        )
        
        if not response or not response.choices or response.choices[0].finish_reason != 'stop':
            print("[ERROR] Errore triage: risposta API vuota o interrotta.")

            # Restituisce un dizionario di default che verrà scartato
            return {"continua_analisi": False, "motivazione": "Risposta API vuota o interrotta."}

        message_content = response.choices[0].message.content
        if not message_content:
            print("[ERROR] Errore triage: contenuto del messaggio vuoto.")
            
            # Restituisce un dizionario di default che verrà scartato
            return {"continua_analisi": False, "motivazione": "Contenuto del messaggio vuoto."}

        json_response = json.loads(message_content)
        return json_response

    except Exception as e:
        print(f"[ERROR] Errore durante l'analisi di triage: {e}")

        # Restituisce un dizionario di default che verrà scartato, con errore interno
        return {"continua_analisi": False, "motivazione": f"Errore interno: {e}"}

# ------------------------------------------------
# Esegue un'analisi olistica e generica di un annuncio (testo, prezzo, immagine)
# basandosi su un contesto di expertise fornito (ai_context_prompt) in una singola chiamata API.
# Restituisce un dizionario JSON con la valutazione complessiva.
# ------------------------------------------------
def doCompleteArticleAnalysis(titolo: str, descrizione: str, prezzo: float, img_url: str, 
                               ai_context_prompt: str, 
                               vendor_username: str, vendor_reviews_count: int) -> dict:

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
    
    # Costruisce il payload del messaggio per l'API, esplicitando 2 ruoli (system, user)
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
    if img_url:
        messages[1]["content"].append({"type": "image_url", "image_url": {"url": img_url}})
    else:
        # Se non c'è immagine, è bene informare esplicitamente l'AI.
        messages[1]["content"][0]["text"] += "\n- Immagine: Non fornita."


    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            response_format={"type": "json_object"},
            messages=messages,
            max_completion_tokens=COMPLETE_ANALYSIS_TOKENS
        )
        
        # Log di debug per monitorare i costi e l'utilizzo dei token.
        print(f"[DEBUG] Tokens: Prompt={response.usage.prompt_tokens}, Completion={response.usage.completion_tokens}")
        
        json_response = json.loads(response.choices[0].message.content)
        return json_response

    except Exception as e:
        # Cattura qualsiasi errore (di rete, API, parsing, etc.) e restituisce una risposta di default per non bloccare il bot.
        print(f"[ERROR] Errore durante l'analisi AI olistica: {e}")
        return {
            "is_interessante": False,
            "punteggio_complessivo": 0,
            "motivazione_complessiva": "Analisi AI fallita o non conclusiva.",
            "parole_chiave": []
        }