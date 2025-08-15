import json
from openai import OpenAI
from config import OPENAI_KEY

client = OpenAI(api_key=OPENAI_KEY)
MODELO_ANALISI = "gpt-5-mini"

def _get_default_response() -> dict:
    """Restituisce una risposta di default non interessante in caso di errore."""
    return {
        "is_interessante": False,
        "punteggio": 0,
        "motivazione": "Analisi AI fallita o non conclusiva.",
        "parole_chiave": []
    }

def _parse_openai_response(response) -> dict:
    """
    Controlla e interpreta la risposta da OpenAI, gestendo casi di errore e contenuto vuoto.
    """
    # 1. Controlla se la risposta o le scelte sono vuote
    if not response or not response.choices:
        print("!!! Errore: Risposta API vuota o senza 'choices'.")
        return _get_default_response()

    choice = response.choices[0]
    
    # 2. Controlla se l'AI è stata interrotta per un motivo specifico (es. filtro contenuti)
    if choice.finish_reason != "stop":
        print(f"!!! Attenzione: Generazione AI interrotta. Motivo: '{choice.finish_reason}'.")
        # Potremmo voler gestire 'content_filter' in modo specifico, ma per ora lo trattiamo come un fallimento.
        return _get_default_response()

    message_content = choice.message.content
    
    # 3. Controlla se il contenuto del messaggio è effettivamente presente
    if not message_content or not message_content.strip():
        print("!!! Errore: Il contenuto del messaggio dall'API è vuoto.")
        return _get_default_response()

    # 4. Solo ora, che siamo sicuri di avere del testo, tentiamo il parsing
    try:
        return json.loads(message_content)
    except json.JSONDecodeError as e:
        print(f"!!! Errore di parsing JSON: {e}. Contenuto ricevuto:\n---START---\n{message_content}\n---END---")
        return _get_default_response()


def analizza_testo_ai(titolo: str, descrizione: str, prezzo: float) -> dict:
    """Analizza titolo, descrizione e prezzo e restituisce un dizionario JSON."""
    # --- PROMPT AVANZATO E PIÙ SELETTIVO ---
    prompt = f"""
    Sei un esperto numismatico molto critico e selettivo. Il tuo obiettivo è scovare solo veri affari, ignorando il resto.
    Analizza il seguente annuncio e restituisci la tua valutazione ESCLUSIVAMENTE in formato JSON, con la solita struttura.
    --- REGOLE DI VALUTAZIONE OBBLIGATORIE ---
    1.  La tua analisi deve basarsi sul RAPPORTO QUALITÀ/PREZZO. Confronta il prezzo dell'annuncio con il valore di mercato *ipotizzato* per gli oggetti descritti. Se è un lotto, stima il prezzo per pezzo e confrontalo.
    2.  Sii PESSIMISTA di default. Un annuncio è "non interessante" fino a prova contraria. Evita l'ottimismo ingiustificato.
    3.  La motivazione deve spiegare CONCRETAMENTE perché il prezzo è un affare o meno, facendo riferimento ai valori di mercato.
    --- VALORI DI MERCATO DI RIFERIMENTO (da usare per la tua analisi) ---
    -   Lira comune del Regno/Repubblica: 0.10 - 0.50 €
    -   Moneta d'argento (es. 500 lire): 5 - 15 € a seconda del peso e conservazione.
    -   2 Euro commemorativo comune: 2.50 - 4 €
    -   Moneta romana comune (non identificata): 1 - 5 €
    --- CRITERI DI PUNTEGGIO RICALIBRATI ---
    -   Punteggio 8-10 (Affare Imperdibile): Solo se il prezzo è SIGNIFICATIVAMENTE INFERIORE al valore di mercato stimato E ci sono forti indicatori di venditore non esperto (es. "lotto del nonno", "eredità"). Esempio: un lotto di 20 monete d'argento a 50€.
    -   Punteggio 5-7 (Potenzialmente Interessante): Il prezzo è leggermente inferiore o in linea con il mercato, ma l'annuncio contiene pezzi degni di nota. Da approfondire.
    -   Punteggio 1-4 (Da Scartare): Il prezzo è in linea con il mercato o superiore. Annunci di singoli pezzi comuni o da venditori professionali. La maggior parte degli annunci rientrerà qui.
    --- DATI DELL'ANNUNCIO DA ANALIZZARE ---
    - Titolo: "{titolo}"
    - Descrizione: "{descrizione}"
    - Prezzo: "{prezzo:.2f} €"
    """
    try:
        response = client.chat.completions.create(
            model=MODELO_ANALISI,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Sei un esperto numismatico che risponde solo con oggetti JSON."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=2000
        )
        print(f"DEBUG USO TESTO: Prompt={response.usage.prompt_tokens}, Completion={response.usage.completion_tokens}")
        # -> Usa la nuova funzione helper per un parsing sicuro
        return _parse_openai_response(response)
        
    except Exception as e:
        print(f"Errore API OpenAI durante la chiamata (testo): {e}")
        return _get_default_response()


def analizza_immagine_ai(img_url: str) -> dict:
    """Analizza l'immagine e restituisce un dizionario JSON."""
    if not img_url:
        return _get_default_response()
    
    prompt = """
    Sei un esperto numismatico molto critico e selettivo. Analizza l'immagine di questo annuncio e restituisci la tua valutazione ESCLUSIVAMENTE in formato JSON, con la solita struttura.
    --- REGOLE DI VALUTAZIONE VISIVA OBBLIGATORIE ---
    1.  Basa il tuo giudizio SOLO su ciò che è chiaramente visibile. Non fare supposizioni su ciò che potrebbe esserci.
    2.  La qualità dell'immagine è un fattore. Una foto sfocata, scura o da cui non si capisce nulla deve ricevere un punteggio bassissimo e 'is_interessante' deve essere false.
    3.  La motivazione deve descrivere gli elementi visivi specifici che giustificano il punteggio.
    --- CRITERI DI PUNTEGGIO VISIVO RICALIBRATI ---
    -   Punteggio 8-10 (Visivamente Eccellente): L'immagine è CHIARA e mostra SENZA DUBBIO la presenza di monete d'argento (riconoscibili dal colore bianco/opaco), o un gran numero (più di 20) di monete ben visibili, o pezzi rari identificabili.
    -   Punteggio 5-7 (Visivamente Interessante): L'immagine mostra un lotto di monete, ma la qualità o la disposizione non permette di essere certi del valore. Si intravede potenziale, ma richiede un'analisi del testo.
    -   Punteggio 1-4 (Visivamente Inutile o Scarso): L'immagine è sfocata, scura, mostra una o due monete comuni, o non fornisce alcuna informazione utile. La maggior parte delle immagini rientrerà qui.
    """
    try:
        response = client.chat.completions.create(
            model=MODELO_ANALISI,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": img_url}}] }],
            max_completion_tokens=2000
        )
        print(f"DEBUG USO IMMAGINE: Prompt={response.usage.prompt_tokens}, Completion={response.usage.completion_tokens}")
        # -> Usa la nuova funzione helper anche qui
        return _parse_openai_response(response)
        
    except Exception as e:
        print(f"Errore API OpenAI durante la chiamata (immagine): {e}")
        return _get_default_response()