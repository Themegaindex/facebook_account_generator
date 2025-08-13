import random
import string
import requests
import hashlib
from faker import Faker

fake = Faker()


def generate_random_string(length: int) -> str:
    """Return a random alphanumeric string of the given length."""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def get_mail_domains():
    """Fetch available mail.tm domains."""
    try:
        res = requests.get("https://api.mail.tm/domains")
        return res.json()['hydra:member'] if res.status_code == 200 else None
    except Exception:
        return None


def create_mail_tm_account():
    """Create a temporary mail.tm account and return credentials and user info."""
    domains = get_mail_domains()
    if domains:
        domain = random.choice(domains)['domain']
        username = generate_random_string(10)
        password = fake.password()
        email = f"{username}@{domain}"
        payload = {"address": email, "password": password}
        res = requests.post("https://api.mail.tm/accounts", json=payload)
        if res.status_code == 201:
            return (
                email,
                password,
                fake.first_name(),
                fake.last_name(),
                fake.date_of_birth(minimum_age=18, maximum_age=45),
            )
    return None, None, None, None, None


def _call(url, params, post: bool = True):
    """Perform an HTTP request to the Facebook API and return JSON response."""
    headers = {
        'User-Agent': '[FBAN/FB4A;FBAV/35.0.0.48.273;FBDM/{density=1.33125,width=800,height=1205};FBLC/en_US;FBPN/com.facebook.katana;FBDV/Nexus 7;FBSV/4.1.1;FBBK/0;]'
    }
    try:
        res = requests.post(url, data=params, headers=headers) if post else requests.get(url, params=params, headers=headers)
        return res.json()
    except Exception:
        return {}


def register_facebook_account(email, password, first_name, last_name, birthday):
    """Register a Facebook account using provided credentials and personal data."""
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
        'return_multiple_errors': True,
    }
    sorted_req = sorted(req.items())
    sig = ''.join(f'{k}={v}' for k, v in sorted_req)
    req['sig'] = hashlib.md5((sig + secret).encode()).hexdigest()
    return _call("https://b-api.facebook.com/method/user.register", req)
