from openai import OpenAI # -> Importa la classe OpenAI
from config import OPENAI_KEY

# -> Crea un'istanza del "client" OpenAI, che gestirà tutte le chiamate API
# La chiave API viene passata qui (o può essere letta automaticamente dalle variabili d'ambiente)
client = OpenAI(api_key=OPENAI_KEY)

def analizza_testo_ai(titolo: str) -> str:
    """Analizza il titolo dell'annuncio con l'AI per una valutazione testuale."""
    prompt = (
        f"Valuta questo annuncio di monete: '{titolo}'. "
        "È un potenziale affare per un collezionista? Indica se sembra un lotto da non esperto "
        "(es. 'eredità', 'monete nonno') o una vendita mirata. Sii sintetico e diretto."
        "Sii estremamente sintetico, rispondi in massimo 50 parole."
    )
    try:
        # -> La sintassi ora è client.chat.completions.create(...)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sei un esperto numismatico che scova affari online."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Restituisce l'errore in un formato leggibile
        return f"Errore API OpenAI (testo): {e}"


def analizza_immagine_ai(img_url: str) -> str:
    """Analizza l'immagine dell'annuncio con l'AI per una valutazione visiva."""
    if not img_url:
        return "Nessuna immagine fornita."
    
    prompt = (
        "Analizza questa foto da un annuncio di monete. "
        "Cerca elementi di valore: monete d'argento (aspetto lucido/opaco tipico), "
        "2 euro commemorativi rari, monete del Regno d'Italia o pezzi antichi. "
        "Se l'immagine è troppo sfocata o inutile, dillo chiaramente."
        "Sii estremamente sintetico, rispondi in massimo 50 parole."
    )
    
    try:
        # -> Anche qui, la sintassi è stata aggiornata
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": img_url,
                            },
                        },
                    ],
                }
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Errore API OpenAI (vision): {e}"