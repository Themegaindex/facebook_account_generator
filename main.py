import requests
import time
from flask import Flask, jsonify
from account_utils import create_mail_tm_account, register_facebook_account

app = Flask(__name__)


# تسجيل الدخول إلى البريد
def login_mail_tm(email, password):
    try:
        res = requests.post("https://api.mail.tm/token", json={"address": email, "password": password})
        return res.json().get('token') if res.status_code == 200 else None
    except Exception as e:
        print(f'[×] Login Error: {e}')
        return None


# انتظار واستلام رسالة فيسبوك
def get_inbox_and_verify(email, token):
    headers = {"Authorization": f"Bearer {token}"}
    print("[*] Waiting for Facebook email...")
    for _ in range(30):
        try:
            res = requests.get("https://api.mail.tm/messages", headers=headers)
            if res.status_code == 200:
                messages = res.json().get('hydra:member', [])
                for msg in messages:
                    if "facebook" in msg['from']['address'].lower():
                        msg_id = msg['id']
                        msg_detail = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=headers)
                        if msg_detail.status_code == 200:
                            content = msg_detail.json().get('text', '')
                            print(f'[+] Facebook Message:\n{content}')
                            return content
        except Exception as e:
            print(f'[×] Inbox Error: {e}')
        time.sleep(5)
    print("[×] No Facebook message received.")
    return None


@app.route('/')
def home():
    return "Welcome to the Facebook Account Generator API"


@app.route('/create_account', methods=['GET'])
def create_account():
    email, password, first_name, last_name, birthday = create_mail_tm_account()
    if email:
        register_facebook_account(email, password, first_name, last_name, birthday)
        return jsonify({
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "birthday": str(birthday)
        })
    return jsonify({"error": "Failed to create account"}), 400


@app.route('/login/<email>/<password>', methods=['GET'])
def login(email, password):
    token = login_mail_tm(email, password)
    if token:
        return jsonify({"token": token})
    return jsonify({"error": "Login failed"}), 400


@app.route('/verify/<email>/<token>', methods=['GET'])
def verify(email, token):
    content = get_inbox_and_verify(email, token)
    if content:
        return jsonify({"message": content})
    return jsonify({"error": "Verification failed"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
