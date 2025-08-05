# Vinted Deal Finder AI

Questo progetto è un agente AI Python progettato per monitorare costantemente il sito di Vinted alla ricerca di annunci di monete da collezione che rappresentino un potenziale affare.

L'agente esegue le seguenti operazioni:
1.  **Scansiona Vinted** a intervalli regolari utilizzando una lista di parole chiave mirate.
2.  **Analizza i risultati** (titolo e immagine dell'annuncio) utilizzando le API di OpenAI (GPT-4o) per valutare se si tratta di un'offerta interessante.
3.  **Invia una notifica istantanea** su Telegram con i dettagli dell'annuncio e l'analisi dell'AI, permettendoti di agire rapidamente.

## Prerequisiti

Prima di iniziare, assicurati di avere:
*   **Python 3.8** o superiore installato sul tuo sistema.
*   Un **account OpenAI** con crediti disponibili per utilizzare le API ([platform.openai.com](https://platform.openai.com/)).
*   Un **account Telegram** per ricevere le notifiche.

## ⚙️ Setup e Installazione

Segui questi passaggi per configurare l'ambiente e installare le dipendenze.

### 1. Clona il Repository (Opzionale)
Se hai scaricato i file manualmente, salta questo passaggio. Altrimenti, clona il repository:
```bash
git clone https://github.com/tuo-utente/deal-finder.git
cd deal-finder
```

### 2. Crea l'Ambiente Virtuale
È una buona pratica isolare le dipendenze del progetto. Esegui questo comando nella cartella principale del progetto:
```bash
python -m venv .venv
```
Verrà creata una cartella `.venv`.

### 3. Attiva l'Ambiente Virtuale
Devi attivare l'ambiente ogni volta che apri un nuovo terminale per lavorare al progetto.

**Su Windows:**

*   **Opzione A (Consigliata - PowerShell):**
    Potrebbe essere necessario abilitare l'esecuzione degli script. Apri PowerShell **come Amministratore** ed esegui:
    ```powershell
    Set-ExecutionPolicy RemoteSigned -Scope Process
    ```
    Successivamente, nel tuo terminale standard (non per forza da amministratore), esegui:
    ```powershell
    .venv\Scripts\activate
    ```

*   **Opzione B (Alternativa Facile - Prompt dei comandi `cmd`):**
    ```cmd
    .venv\Scripts\activate.bat
    ```

**Su macOS / Linux:**
```bash
source .venv/bin/activate
```
Una volta attivato, vedrai `(.venv)` all'inizio della riga del tuo terminale.

### 4. Installa i Requisiti
Con l'ambiente virtuale attivo, installa tutte le librerie necessarie con un solo comando:
```bash
pip install -r requirements.txt
```

## 🔧 Configurazione
Tutte le configurazioni, comprese le chiavi segrete, si trovano nel file `config.py`.

1.  Apri il file `config.py`.
2.  Inserisci i seguenti valori:
    *   `TELEGRAM_TOKEN`: Il token del tuo bot Telegram. Puoi ottenerlo parlando con [@BotFather](https://t.me/botfather) su Telegram.
    *   `TELEGRAM_CHAT_ID`: Il tuo ID utente univoco su Telegram. Puoi ottenerlo scrivendo `/start` a un bot come `@userinfobot`.
    *   `OPENAI_KEY`: La tua chiave API segreta di OpenAI. La trovi nella dashboard del tuo account OpenAI.
3.  (Opzionale) Puoi personalizzare la lista `SEARCH_TERMS` e il tempo di attesa `WAIT_TIME_SECONDS` secondo le tue preferenze.

## ▶️ Avvio dell'Agente
Una volta completata la configurazione, assicurati che il tuo ambiente virtuale sia attivo e avvia lo script principale:
```bash
python main.py
```
L'agente inizierà a scansionare Vinted e a inviare notifiche al tuo canale Telegram.

## 📂 Struttura del Progetto
```
deal-finder/
├── config.py         # Configurazioni e chiavi API
├── requirements.txt  # Dipendenze Python
├── scraper.py        # Logica per lo scraping di Vinted
├── analyzer.py       # Logica per l'analisi con OpenAI
├── notifier.py       # Logica per le notifiche Telegram
└── main.py           # Script principale che orchestra il tutto
```

## ⚠️ Disclaimer
Questo script è stato creato per scopi didattici e dimostrativi. Lo scraping automatico potrebbe violare i Termini di Servizio di Vinted. Utilizzalo a tuo rischio e in modo responsabile, evitando di sovraccaricare il sito con richieste troppo frequenti. Gli sviluppatori non si assumono alcuna responsabilità per un uso improprio dello script.