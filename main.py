import os
import sys
from generator_lib import api
from dotenv import load_dotenv

def main():
    """
    Ein einfaches CLI-Tool zum Generieren eines einzelnen Facebook-Kontos.
    Die erforderlichen Umgebungsvariablen FACEBOOK_API_KEY und FACEBOOK_SECRET
    müssen gesetzt sein.
    """
    # Umgebungsvariablen aus .env-Datei laden
    load_dotenv()

    print("=============================================")
    print("=== Facebook Account Generator (CLI-Modus) ===")
    print("=============================================")

    # Überprüfen, ob die API-Schlüssel vorhanden sind
    if not os.environ.get('FACEBOOK_API_KEY') or not os.environ.get('FACEBOOK_SECRET'):
        print("\n[×] FEHLER: Die Umgebungsvariablen FACEBOOK_API_KEY und FACEBOOK_SECRET sind nicht gesetzt.")
        print("Bitte erstellen Sie eine .env-Datei oder exportieren Sie die Variablen.")
        sys.exit(1) # Beendet das Skript mit einem Fehlercode

    # Schritt 1: Temporäre E-Mail erstellen
    print("\n[1] Erstelle temporäre E-Mail-Adresse...")
    account_data = api.create_mail_tm_account()
    if not all(account_data):
        print("[×] E-Mail-Erstellung fehlgeschlagen. Breche ab.")
        sys.exit(1)

    email, password, first_name, last_name, birthday = account_data
    print(f"[√] E-Mail erstellt: {email}")
    print(f"[+] Passwort: {password}")

    # Schritt 2: Facebook-Konto registrieren
    print("\n[2] Versuche, Facebook-Konto zu registrieren...")
    fb_response = api.register_facebook_account(email, password, first_name, last_name, birthday)
    print(f"[+] Facebook API-Antwort: {fb_response}")

    # Schritt 3: E-Mail-Verifizierung
    print("\n[3] Suche nach Verifizierungs-E-Mail (ca. 30 Sekunden)...")
    verification_content, verification_status = api.get_inbox_and_verify(email, password)
    print(f"[+] Verifizierungsstatus: {verification_status}")
    if verification_content:
        print(f"[+] E-Mail-Inhalt: {verification_content[:200]}...") # Gekürzter Inhalt

    # Ergebnisse zusammenfassen
    print("\n=================== ERGEBNIS ===================")
    print(f"Name      : {first_name} {last_name}")
    print(f"Geburtstag: {birthday.strftime('%d.%m.%Y')}")
    print(f"E-Mail    : {email}")
    print(f"Passwort  : {password}")
    print("---------------------------------------------")

    if fb_response and 'error' not in fb_response:
        print("[√] Facebook-Registrierung scheint erfolgreich gewesen zu sein (laut API).")
        print(f"   - User ID: {fb_response.get('new_user_id')}")
        print(f"   - Access Token: {fb_response.get('session_info', {}).get('access_token')}")
    else:
        print("[×] Facebook-Registrierung fehlgeschlagen.")
        print(f"   - Grund: {fb_response.get('error', 'Unbekannter Fehler')}")

    print(f"E-Mail-Verifizierung: {verification_status}")
    print("=============================================")


if __name__ == '__main__':
    main()
