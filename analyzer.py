import json # -> Importato per parsare la risposta dell'AI
from openai import OpenAI
from config import OPENAI_KEY

client = OpenAI(api_key=OPENAI_KEY)
MODELO_ANALISI = "gpt-5-mini" 

# Ho usato gpt-4o nel mio esempio precedente per la sua affidabilità con i JSON.
# Se gpt-5-mini dovesse avere problemi a generare JSON validi,
# questo è il primo modello da provare come alternativa.
# MODELO_ANALISI_JSON_RELIABLE = "gpt-4o" 

def _get_default_response() -> dict:
    """Restituisce una risposta di default non interessante in caso di errore."""
    return {
        "is_interessante": False,
        "punteggio": 0,
        "motivazione": "Analisi AI fallita o non conclusiva.",
        "parole_chiave": []
    }

def analizza_testo_ai(titolo: str, descrizione: str) -> dict:
    """
    Analizza titolo e descrizione e restituisce un dizionario JSON con la valutazione.
    """
    prompt = f"""
    Analizza il seguente annuncio di monete e restituisci la tua valutazione ESCLUSIVAMENTE in formato JSON.
    Il JSON deve avere questa struttura:
    {{
      "is_interessante": boolean,
      "punteggio": integer (1-10),
      "motivazione": "stringa di testo (massimo 70 parole)",
      "parole_chiave": ["lista", "di", "stringhe"]
    }}

    Valuta l'annuncio basandoti su questi criteri:
    - 'is_interessante' deve essere true se ritieni che l'annuncio sia di valore, ovvero il prezzo di acquisto è vantaggioso e inferiore al valore di mercato atteso per l'annuncio.
    - Assegna un punteggio alto (8-10) per annunci di valore interessante, a seconda dell'interesse. 
    - Aumenta di 1 o 2 punti se l'annuncio sembra scritto da venditore non esperto.
    - Assegna un punteggio medio (5-7) per annunci specifici ma interessanti.
    - Assegna un punteggio basso (1-4) per annunci singoli di poco valore, monete comuni o da venditori professionali.
    - La motivazione deve spiegare brevemente perché l'annuncio è (o non è) interessante.

    Dati dell'annuncio:
    - Titolo: "{titolo}"
    - Descrizione: "{descrizione}"
    """
    try:
        response = client.chat.completions.create(
            model=MODELO_ANALISI,
            # -> Istruisce l'AI a rispondere in formato JSON. È più affidabile del solo prompt.
            response_format={"type": "json_object"}, 
            messages=[
                {"role": "system", "content": "Sei un esperto numismatico che risponde solo con oggetti JSON validi."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=1250
        )
        
        # Manteniamo il tuo debug dei token, è molto utile.
        print(f"DEBUG USO TESTO: Prompt={response.usage.prompt_tokens}, Completion={response.usage.completion_tokens}")

        # Estraiamo e parsiamo la stringa JSON dalla risposta
        json_response = json.loads(response.choices[0].message.content)
        return json_response

    except Exception as e:
        print(f"Errore durante l'analisi AI del testo o nel parsing JSON: {e}")
        return _get_default_response()


def analizza_immagine_ai(img_url: str) -> dict:
    """Analizza l'immagine e restituisce un dizionario JSON con la valutazione."""
    if not img_url:
        return _get_default_response()
    
    prompt = """
    Analizza l'immagine di questo annuncio di monete e restituisci la tua valutazione ESCLUSIVAMENTE in formato JSON, con la stessa struttura di prima:
    {"is_interessante": boolean, "punteggio": integer (1-10), "motivazione": "stringa", "parole_chiave": []}.

    - 'is_interessante' deve essere true se vedi monete di valore il cui prezzo di vendita è inferiore al prezzo medio del mercato.
    - Se l'immagine è sfocata, inutile o mostra una singola moneta comune, imposta 'is_interessante' a false.
    - Fornisci un punteggio e una breve motivazione.
    """
    try:
        response = client.chat.completions.create(
            model=MODELO_ANALISI,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": img_url}},
                    ],
                }
            ],
            max_completion_tokens=1250
        )
        
        # Corretto il nome del print di debug per distinguerlo
        print(f"DEBUG USO IMMAGINE: Prompt={response.usage.prompt_tokens}, Completion={response.usage.completion_tokens}")

        json_response = json.loads(response.choices[0].message.content)
        return json_response
        
    except Exception as e:
        print(f"Errore durante l'analisi AI dell'immagine o nel parsing JSON: {e}")
        return _get_default_response()