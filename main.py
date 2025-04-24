import requests
import random
import string
import json
import hashlib
import time
from faker import Faker
from flask import Flask, jsonify

app = Flask(__name__)

# توليد سلسلة عشوائية
def generate_random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

# جلب نطاقات البريد
def get_mail_domains():
    try:
        res = requests.get("https://api.mail.tm/domains")
        return res.json()['hydra:member'] if res.status_code == 200 else None
    except Exception as e:
        print(f'[×] Domain Error : {e}')
        return None

# إنشاء بريد مؤقت
def create_mail_tm_account():
    fake = Faker()
    domains = get_mail_domains()
    if domains:
        domain = random.choice(domains)['domain']
        username = generate_random_string(10)
        password = fake.password()
        email = f"{username}@{domain}"
        payload = {"address": email, "password": password}
        try:
            res = requests.post("https://api.mail.tm/accounts", json=payload)
            if res.status_code == 201:
                print(f'[√] Email Created: {email}')
                return email, password, fake.first_name(), fake.last_name(), fake.date_of_birth(minimum_age=18, maximum_age=45)
            else:
                print(f'[×] Account Creation Error: {res.text}')
        except Exception as e:
            print(f'[×] Account Exception: {e}')
    return None, None, None, None, None

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

# إنشاء حساب فيسبوك
def register_facebook_account(email, password, first_name, last_name, birthday):
    api_key = '882a8490361da98702bf97a021ddc14d'
    secret = '62f8ce9f74b12f84c123cc23437a4a32'
    gender = random.choice(['M', 'F'])
    req = {
        'api_key': api_key,
        'attempt_login': True,
        'birthday': birthday.strftime('%Y-%m-%d'),
        'client_country_code': 'EN',
        'fb_api_caller_class': 'com.facebook.registration.protocol.RegisterAccountMethod',
        'fb_api_req_friendly_name': 'registerAccount',
        'firstname': first_name,
        'format': 'json',
        'gender': gender,
        'lastname': last_name,
        'email': email,
        'locale': 'en_US',
        'method': 'user.register',
        'password': password,
        'reg_instance': generate_random_string(32),
        'return_multiple_errors': True
    }
    sorted_req = sorted(req.items())
    sig = ''.join(f'{k}={v}' for k, v in sorted_req)
    req['sig'] = hashlib.md5((sig + secret).encode()).hexdigest()
    response = _call("https://b-api.facebook.com/method/user.register", req)
    print(f'[×] Facebook API Response: {response}')
    if 'new_user_id' in response and 'session_info' in response and 'access_token' in response['session_info']:
        print(f'''
[+] Email     : {email}
[+] Name      : {first_name} {last_name}
[+] Birthday  : {birthday}
[+] Gender    : {gender}
[+] Password  : {password}
[+] User ID   : {response["new_user_id"]}
[+] Token     : {response["session_info"]["access_token"]}
============================================''')
    else:
        print('[×] Registration Failed.')

# الاتصال بواجهة Facebook API
def _call(url, params, post=True):
    headers = {
        'User-Agent': '[FBAN/FB4A;FBAV/35.0.0.48.273;FBDM/{density=1.33125,width=800,height=1205};FBLC/en_US;FBPN/com.facebook.katana;FBDV/Nexus 7;FBSV/4.1.1;FBBK/0;]'
    }
    try:
        res = requests.post(url, data=params, headers=headers) if post else requests.get(url, params=params, headers=headers)
        return res.json()
    except Exception as e:
        print(f'[×] API Call Failed: {e}')
        return {}

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
