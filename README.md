# Glovo Price Monitor

Rileva automaticamente errori di prezzo al ribasso su Glovo usando dati reali via Apify.

## Deploy su Render (gratis)

### 1. Crea un account GitHub
Se non ce l'hai: https://github.com/signup (gratuito)

### 2. Crea un repository GitHub
1. Vai su https://github.com/new
2. Nome: glovo-monitor, visibilità: Private
3. Carica tutti i file di questa cartella nel repo

### 3. Crea un account Render
Vai su https://render.com e registrati (gratuito)

### 4. Crea un nuovo Web Service
1. Dashboard → New → Web Service
2. Collega GitHub e seleziona il repo glovo-monitor
3. Compila:
   - Runtime: Python
   - Build Command: pip install -r requirements.txt
   - Start Command: gunicorn server:app
   - Plan: Free
4. Clicca Advanced → Add Environment Variable:
   - APIFY_TOKEN = il tuo token Apify
   - ANTHROPIC_API_KEY = la tua chiave (opzionale)
5. Create Web Service → aspetta 2-3 minuti

Otterrai un URL tipo: https://glovo-monitor.onrender.com

## Token necessari

Token Apify (obbligatorio):
- Registrati su https://apify.com (piano free: $5/mese crediti)
- Vai su https://console.apify.com/account/integrations
- Costo indicativo: ~$0.10-0.50 per scansione da 200 prodotti

API Key Anthropic (opzionale, per analisi AI):
- https://console.anthropic.com/keys

## Uso in locale

  pip install -r requirements.txt
  APIFY_TOKEN=tuo_token python server.py
  # poi apri http://localhost:5000
