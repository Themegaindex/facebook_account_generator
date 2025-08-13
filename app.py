from flask import Flask, render_template, request
import requests, random, string, json, hashlib, time
import logging
from faker import Faker
from datetime import datetime

app = Flask(__name__)
fake = Faker()

logging.basicConfig(level=logging.ERROR)

def generate_random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def get_mail_domains():
    try:
        res = requests.get("https://api.mail.tm/domains", timeout=10)
        return res.json()['hydra:member'] if res.status_code == 200 else None
    except requests.Timeout as e:
        logging.error(f'Domain Timeout: {e}')
    except Exception as e:
        logging.error(f'Domain Error: {e}')
    return None

def create_mail_tm_account():
    domains = get_mail_domains()
    if domains:
        domain = random.choice(domains)['domain']
        username = generate_random_string(10)
        password = fake.password()
        email = f"{username}@{domain}"
        payload = {"address": email, "password": password}
        try:
            res = requests.post("https://api.mail.tm/accounts", json=payload, timeout=10)
            if res.status_code == 201:
                return email, password, fake.first_name(), fake.last_name(), fake.date_of_birth(minimum_age=18, maximum_age=45)
            else:
                logging.error(f'Account Creation Error: {res.text}')
        except requests.Timeout as e:
            logging.error(f'Account Timeout: {e}')
        except Exception as e:
            logging.error(f'Account Error: {e}')
    return None, None, None, None, None

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
    return _call("https://b-api.facebook.com/method/user.register", req)

def _call(url, params, post=True):
    headers = {
        'User-Agent': '[FBAN/FB4A;FBAV/35.0.0.48.273;FBDM/{density=1.33125,width=800,height=1205};FBLC/en_US;FBPN/com.facebook.katana;FBDV/Nexus 7;FBSV/4.1.1;FBBK/0;]'
    }
    try:
        res = requests.post(url, data=params, headers=headers, timeout=10) if post else requests.get(url, params=params, headers=headers, timeout=10)
        return res.json()
    except requests.Timeout as e:
        logging.error(f'API Call Timeout: {e}')
    except Exception as e:
        logging.error(f'API Call Failed: {e}')
    return {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        count = int(request.form['count'])
        results = []
        for _ in range(count):
            email, password, first_name, last_name, birthday = create_mail_tm_account()
            if email:
                fb_response = register_facebook_account(email, password, first_name, last_name, birthday)
                results.append({
                    'email': email,
                    'password': password,
                    'name': f"{first_name} {last_name}",
                    'birthday': birthday.strftime('%Y-%m-%d'),
                    'response': fb_response
                })
        return render_template('result.html', results=results)
    except Exception as e:
        return f"حدث خطأ: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
