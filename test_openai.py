import sys
from config import OPENAI_KEY # Importa la chiave per il controllo iniziale
from analyzer import analizza_testo_ai, analizza_immagine_ai

# --- DATI DI ESEMPIO PER IL TEST ---

# Esempio di titolo di un annuncio per testare l'analisi testuale
TEST_TITLE = "Lotto monete vecchie trovate in cantina da mio nonno"

# URL di un'immagine di monete per testare l'analisi visiva (Vision API)
# Questa è un'immagine di esempio trovata online.
TEST_IMAGE_URL = "https://i.ebayimg.com/images/g/s~MAAOSwqMRk3F6p/s-l1600.jpg"

print (f"OPENAI_KEY:  '{OPENAI_KEY}'")

def test_openai_integration():
    """
    Esegue un test completo delle funzionalità di analisi testuale e visiva
    utilizzando le API di OpenAI per verificare la corretta integrazione.
    """
    # Controllo preliminare per assicurarsi che la chiave sia stata caricata
    if not OPENAI_KEY:
        print("🛑 ERRORE: La chiave API di OpenAI non è stata trovata.")
        print("Assicurati che sia definita correttamente nel tuo file .env e che config.py la carichi.")
        sys.exit(1)
        
    print("--- Inizio test di integrazione con le API di OpenAI ---")

    # --- 1. TEST ANALISI TESTUALE ---
    print("\n[1/2] Sto testando l'analisi del testo con GPT-4o...")
    try:
        valutazione_testo = analizza_testo_ai(TEST_TITLE)
        
        print(f"✅ Successo! L'API di analisi testuale ha risposto.")
        print("-" * 20)
        print(f"Prompt inviato (implicito): Analisi del titolo '{TEST_TITLE}'")
        print(f"Risposta dell'AI: {valutazione_testo}")
        print("-" * 20)
        
    except Exception as e:
        print(f"\n❌ ERRORE durante il test di analisi del testo.")
        print(f"Dettagli dell'errore: {e}")
        print("Controlla la tua chiave API e lo stato dei servizi di OpenAI.")
        return # Interrompe il test se questa parte fallisce

    # --- 2. TEST ANALISI IMMAGINE (VISION) ---
    print("\n[2/2] Sto testando l'analisi dell'immagine con GPT-4o (Vision)...")
    try:
        valutazione_img = analizza_immagine_ai(TEST_IMAGE_URL)
        
        print(f"\n✅ Successo! L'API di analisi visiva (Vision) ha risposto.")
        print("-" * 20)
        print(f"Immagine analizzata: {TEST_IMAGE_URL}")
        print(f"Risposta dell'AI: {valutazione_img}")
        print("-" * 20)
        
    except Exception as e:
        print(f"\n❌ ERRORE durante il test di analisi dell'immagine.")
        print(f"Dettagli dell'errore: {e}")
        print("Verifica che il tuo piano OpenAI supporti il modello GPT-4o e le Vision API.")
        return
        
    print("\n🎉 Test di integrazione con OpenAI completato con successo! 🎉")

if __name__ == "__main__":
    test_openai_integration()