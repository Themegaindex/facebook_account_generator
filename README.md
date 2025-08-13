# 🌐 Facebook Account Generator

Ein kleines Projekt zum experimentellen Erstellen von Testkonten für Facebook. 
Es nutzt die [mail.tm](https://mail.tm) API für temporäre E-Mail-Adressen und 
das inoffizielle **Facebook API**-Register-Endpunkt.

> ⚠️ Dieses Projekt dient ausschließlich zu Forschungs- und Ausbildungszwecken. 
> Verwende es nicht für Spam oder gegen die Richtlinien von Facebook.

## ✨ Funktionen
- 📧 Automatisches Erstellen temporärer E-Mail-Adressen
- 👤 Generieren zufälliger Nutzerdaten mit [Faker](https://faker.readthedocs.io/)
- 🔐 Registrieren von Facebook-Testkonten via API
- 🌍 Weboberfläche zur Generierung mehrerer Konten
- 🧩 REST-Endpunkte zur Integration in andere Tools

## 📦 Voraussetzungen
- Python 3.9+
- `pip` zum Installieren von Abhängigkeiten

## 🛠 Installation
```bash
pip install -r requirements.txt
```

## 🚀 Nutzung
### Weboberfläche
```bash
python app.py
```
Öffne danach [http://localhost:5000](http://localhost:5000) und gib die Anzahl der zu 
erstellenden Konten ein.

### REST-API
```bash
python main.py
```
Verfügbare Endpunkte:
- `GET /` – Willkommenstext
- `GET /create_account` – Erstellt ein Konto und gibt JSON mit den Daten zurück
- `GET /login/<email>/<passwort>` – Login in mail.tm
- `GET /verify/<email>/<token>` – Wartet auf eine Facebook-Bestätigungsmail

## 🧪 Beispielantwort
```json
{
  "email": "example@domain.com",
  "password": "Passw0rd!",
  "first_name": "John",
  "last_name": "Doe",
  "birthday": "1990-01-01"
}
```

## 📄 Lizenz
Dieses Projekt steht unter der MIT-Lizenz. Siehe `LICENSE`, falls vorhanden.

Viel Spaß beim Ausprobieren! 😄

