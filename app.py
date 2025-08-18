from flask import Flask, render_template, request
from generator_lib import api
import os

# Laden der Umgebungsvariablen aus einer .env-Datei (optional, für die Entwicklung)
# In einer Produktionsumgebung sollten diese Variablen direkt gesetzt werden.
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    """Zeigt die Startseite mit dem Formular an."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Verarbeitet die Formulareingabe, um Konten zu generieren."""
    results = []
    try:
        # Sicherstellen, dass die API-Schlüssel vorhanden sind, bevor wir anfangen
        if not os.environ.get('FACEBOOK_API_KEY') or not os.environ.get('FACEBOOK_SECRET'):
            return "Fehler: FACEBOOK_API_KEY und FACEBOOK_SECRET müssen als Umgebungsvariablen gesetzt sein.", 500

        count = int(request.form['count'])

        for i in range(count):
            print(f"--- Starte Generierung für Konto {i+1}/{count} ---")

            # Schritt 1: Temporäre E-Mail erstellen
            account_data = api.create_mail_tm_account()
            if not all(account_data):
                print("[×] E-Mail-Erstellung fehlgeschlagen.")
                results.append({
                    'status': 'Fehlgeschlagen',
                    'message': 'Konnte keine temporäre E-Mail erstellen.'
                })
                continue # Nächsten Versuch starten

            email, password, first_name, last_name, birthday = account_data

            # Schritt 2: Facebook-Konto registrieren
            print(f"[*] Versuche, Facebook-Konto für {email} zu registrieren...")
            fb_response = api.register_facebook_account(email, password, first_name, last_name, birthday)

            # Schritt 3: E-Mail-Verifizierung (unabhängig vom FB-API-Ergebnis)
            print(f"[*] Suche nach Verifizierungs-E-Mail für {email}...")
            verification_content, verification_status = api.get_inbox_and_verify(email, password)

            results.append({
                'status': 'Abgeschlossen',
                'email': email,
                'password': password,
                'name': f"{first_name} {last_name}",
                'birthday': birthday.strftime('%d.%m.%Y'),
                'fb_response': fb_response,
                'verification_status': verification_status
            })
            print("--- Generierung abgeschlossen ---")

        return render_template('result.html', results=results)

    except Exception as e:
        # Allgemeiner Fehler-Fallback
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        return f"Ein unerwarteter Fehler ist aufgetreten: {str(e)}", 500

if __name__ == '__main__':
    # Stellt sicher, dass die App im Debug-Modus läuft, wenn sie direkt ausgeführt wird
    # Host auf 0.0.0.0 setzen, um von außerhalb des Containers erreichbar zu sein (falls zutreffend)
    app.run(debug=True, host='0.0.0.0', port=5000)
