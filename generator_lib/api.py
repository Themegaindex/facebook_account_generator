import requests
import random
import string
import json
import hashlib
import time
import os
from faker import Faker
from datetime import datetime

def generate_random_string(length):
    """Generiert eine zufällige Zeichenfolge der angegebenen Länge."""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def get_mail_domains():
    """Ruft verfügbare E-Mail-Domains von der mail.tm-API ab."""
    try:
        res = requests.get("https://api.mail.tm/domains", timeout=10)
        res.raise_for_status()
        return res.json()['hydra:member']
    except requests.exceptions.RequestException as e:
        print(f'[×] Domain-Fehler: {e}')
        return None

def create_mail_tm_account():
    """Erstellt ein temporäres E-Mail-Konto mit mail.tm."""
    fake = Faker()
    domains = get_mail_domains()
    if domains:
        domain = random.choice(domains)['domain']
        username = generate_random_string(10)
        password = fake.password()
        email = f"{username}@{domain}"
        payload = {"address": email, "password": password}
        try:
            res = requests.post("https://api.mail.tm/accounts", json=payload, timeout=10)
            res.raise_for_status()
            if res.status_code == 201:
                print(f'[√] E-Mail erstellt: {email}')
                birthday = fake.date_of_birth(minimum_age=18, maximum_age=45)
                return email, password, fake.first_name(), fake.last_name(), birthday
        except requests.exceptions.RequestException as e:
            print(f'[×] Fehler bei der Kontoerstellung: {e}')
    return None, None, None, None, None

def login_mail_tm(email, password):
    """Meldet sich beim mail.tm-Konto an, um ein Token zu erhalten."""
    try:
        res = requests.post("https://api.mail.tm/token", json={"address": email, "password": password}, timeout=10)
        res.raise_for_status()
        return res.json().get('token')
    except requests.exceptions.RequestException as e:
        print(f'[×] Anmeldefehler: {e}')
        return None

def get_inbox_and_verify(email, password):
    """Überprüft den Posteingang auf die Facebook-Bestätigungs-E-Mail."""
    token = login_mail_tm(email, password)
    if not token:
        return None, "Anmeldung bei E-Mail fehlgeschlagen"

    headers = {"Authorization": f"Bearer {token}"}
    print("[*] Warte auf Facebook-E-Mail...")
    for _ in range(6): # 30 Sekunden warten (6 * 5s)
        try:
            res = requests.get("https://api.mail.tm/messages", headers=headers, timeout=10)
            res.raise_for_status()
            messages = res.json().get('hydra:member', [])
            for msg in messages:
                if "facebook" in msg['from']['address'].lower():
                    msg_id = msg['id']
                    msg_detail_res = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=headers, timeout=10)
                    msg_detail_res.raise_for_status()
                    content = msg_detail_res.json().get('text', '')
                    print(f'[+] Facebook-Nachricht empfangen.')
                    return content, "Verifizierung erfolgreich"
        except requests.exceptions.RequestException as e:
            print(f'[×] Posteingangsfehler: {e}')
        time.sleep(5)

    print("[×] Keine Facebook-Nachricht empfangen.")
    return None, "Keine Verifizierungs-E-Mail von Facebook erhalten."

def register_facebook_account(email, password, first_name, last_name, birthday):
    """Versucht, ein Facebook-Konto zu registrieren."""
    api_key = os.environ.get('FACEBOOK_API_KEY')
    secret = os.environ.get('FACEBOOK_SECRET')

    if not api_key or not secret:
        return {"error": "API-Schlüssel oder Secret nicht in Umgebungsvariablen gefunden."}

    gender = random.choice(['M', 'F'])
    req = {
        'api_key': api_key,
        'attempt_login': True,
        'birthday': birthday.strftime('%Y-%m-%d'),
        'client_country_code': 'DE',
        'fb_api_caller_class': 'com.facebook.registration.protocol.RegisterAccountMethod',
        'fb_api_req_friendly_name': 'registerAccount',
        'firstname': first_name,
        'format': 'json',
        'gender': gender,
        'lastname': last_name,
        'email': email,
        'locale': 'de_DE',
        'method': 'user.register',
        'password': password,
        'reg_instance': generate_random_string(32),
        'return_multiple_errors': True
    }

    sorted_req = sorted(req.items())
    sig = ''.join(f'{k}={v}' for k, v in sorted_req)
    req['sig'] = hashlib.md5((sig + secret).encode()).hexdigest()

    return _call("https://b-api.facebook.com/method/user.register", req)

def _call(url, params, post=True):
    """Führt den API-Aufruf an die Facebook-API durch."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        if post:
            res = requests.post(url, data=params, headers=headers, timeout=10)
        else:
            res = requests.get(url, params=params, headers=headers, timeout=10)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API-Aufruf fehlgeschlagen: {e}"}
    except json.JSONDecodeError:
        return {"error": "Ungültige JSON-Antwort von der API."}
