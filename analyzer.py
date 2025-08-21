import json
from openai import OpenAI
from config import OPENAI_KEY

client = OpenAI(api_key=OPENAI_KEY)
MODELO_ANALISI = "gpt-5-mini"

def _get_default_response() -> dict:
    """Restituisce una risposta di default non interessante in caso di errore."""
    return {
        "is_interessante": False,
        "punteggio_complessivo": 0,
        "motivazione_complessiva": "Analisi AI fallita o non conclusiva.",
        "parole_chiave": []
    }

def analizza_annuncio_completo(titolo: str, descrizione: str, prezzo: float, img_url: str) -> dict:
    """
    Esegue un'analisi olistica di un annuncio (testo, prezzo, immagine) in una singola chiamata API
    e restituisce un dizionario JSON con la valutazione complessiva.
    """
    # --- PROMPT OLISTICO E FINALE ---
    prompt = f"""
    Sei un esperto numismatico molto critico e selettivo. Il tuo obiettivo è scovare solo veri affari.
    Analizza l'annuncio completo (testo e immagine) e restituisci una valutazione OLISTICA.
    La tua risposta deve essere ESCLUSIVAMENTE in formato JSON con questa struttura:
    {{
      "is_interessante": boolean,
      "punteggio_complessivo": integer (1-10),
      "motivazione_complessiva": "stringa di testo (massimo 80 parole)",
      "parole_chiave": ["lista", "di", "stringhe"]
    }}

    --- REGOLE DI VALUTAZIONE OLISTICA OBBLIGATORIE ---
    1.  La tua valutazione deve combinare TUTTE le informazioni: testo, descrizione, prezzo E immagine.
    2.  Un'immagine di bassa qualità può essere compensata da un testo eccellente (es. "lotto argento" a basso prezzo), e viceversa. La tua motivazione deve riflettere questo bilanciamento.
    3.  Sii PESSIMISTA di default. Usa i valori di mercato di riferimento per giudicare il prezzo.
        - Lira comune: 0.10€, Moneta argento: 5-15€, 2€ comm. comune: 3€, Romana comune: 1-5€.
    4.  Motiva la tua decisione finale basandoti su come tutti gli elementi interagiscono tra loro.

    --- CRITERI DI PUNTEGGIO COMPLESSIVO ---
    -   Punteggio 8-10 (Affare Imperdibile): Tutti gli indicatori sono positivi. Testo promettente (lotto, eredità), prezzo palesemente basso E immagine che conferma (tante monete, argento visibile).
    -   Punteggio 5-7 (Potenzialmente Interessante): Indicatori contrastanti. Es: testo ottimo ma foto brutta, o viceversa. Vale la pena approfondire.
    -   Punteggio 1-4 (Da Scartare): Annuncio debole. Prezzo alto, descrizione scarsa o foto inutile. La maggior parte degli annunci rientrerà qui.

    --- DATI DELL'ANNUNCIO DA ANALIZZARE ---
    - Titolo: "{titolo}"
    - Descrizione: "{descrizione}"
    - Prezzo: "{prezzo:.2f} €"
    """
    
    # Costruisci il messaggio per l'API con testo e immagine
    messages = [
        {
            "role": "system",
            "content": "Sei un esperto numismatico critico che analizza annunci completi e risponde solo con oggetti JSON."
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt}
            ]
        }
    ]
    # Aggiungi l'URL dell'immagine solo se è valido
    if img_url:
        messages[1]["content"].append({"type": "image_url", "image_url": {"url": img_url}})
    else:
        # Se non c'è immagine, lo diciamo all'AI
        messages[1]["content"][0]["text"] += "\n- Immagine: Non fornita."


    try:
        response = client.chat.completions.create(
            model=MODELO_ANALISI,
            response_format={"type": "json_object"},
            messages=messages,
            max_completion_tokens=2000
        )
        print(f"DEBUG USO COMBINATO: Prompt={response.usage.prompt_tokens}, Completion={response.usage.completion_tokens}")
        # Usiamo un parsing sicuro (anche se il JSON format aiuta)
        json_response = json.loads(response.choices[0].message.content)
        return json_response
    except Exception as e:
        print(f"Errore durante l'analisi AI olistica: {e}")
        return _get_default_response()