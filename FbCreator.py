import threading
from queue import Queue
import requests
import random
import string
import json
import hashlib
import time
import re
from faker import Faker

print(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓           
> › Github :- @Xio
> › By      :- Rey Estacio
> › Proxy Support Added by @coopers-lab
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛                
""")
print('\x1b[38;5;208m⇼'*60)
print('\x1b[38;5;22m•'*60)
print('\x1b[38;5;22m•'*60)
print('\x1b[38;5;208m⇼'*60)

FAKE = Faker()

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_1secmail_account():
    """Creates a temporary email account with 1secmail."""
    username = generate_random_string(10)
    domains = ["1secmail.com", "1secmail.org", "1secmail.net"]
    email = f"{username}@{random.choice(domains)}"
    
    password = FAKE.password()
    birthday = FAKE.date_of_birth(minimum_age=18, maximum_age=45)
    first_name = FAKE.first_name()
    last_name = FAKE.last_name()

    return email, password, first_name, last_name, birthday

def get_1secmail_verification_code(email):
    """Fetches the verification code from 1secmail inbox."""
    login, domain = email.split("@")
    inbox_url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"

    for _ in range(10):  # Try for 10 seconds
        try:
            inbox_response = requests.get(inbox_url)
            messages = inbox_response.json()
            
            if messages:
                latest_email_id = messages[0]["id"]
                message_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={latest_email_id}"
                message_response = requests.get(message_url)
                
                if message_response.status_code == 200:
                    content = message_response.json().get("body", "")
                    code_match = re.search(r'\b\d{6}\b', content)  # Assuming a 6-digit code
                    if code_match:
                        return code_match.group()
        except Exception as e:
            print(f"[×] Error fetching email: {e}")

        time.sleep(2)

    return None

def register_facebook_account(email, password, first_name, last_name, birthday, proxy=None):
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

    sorted_req = sorted(req.items(), key=lambda x: x[0])
    sig = ''.join(f'{k}={v}' for k, v in sorted_req)
    ensig = hashlib.md5((sig + secret).encode()).hexdigest()
    req['sig'] = ensig

    api_url = 'https://b-api.facebook.com/method/user.register'
    reg = _call(api_url, req, proxy)

    id = reg.get('new_user_id', 'REGISTRATION FAILED')
    token = reg.get('session_info', {}).get('access_token', 'N/A')

    if id == 'REGISTRATION FAILED':
        print("[×] Facebook registration failed. Response:", reg)

    verification_code = get_1secmail_verification_code(email)

    print(f'''
-----------GENERATED-----------
EMAIL     : {email}
ID        : {id}
PASSWORD  : {password}
NAME      : {first_name} {last_name}
BIRTHDAY  : {birthday} 
GENDER    : {gender}
VERIFICATION CODE: {verification_code if verification_code else 'N/A'}
-----------GENERATED-----------
Token     : {token}
-----------GENERATED-----------''')

def _call(url, params, proxy=None, post=True):
    headers = {
        'User-Agent': '[FBAN/FB4A;FBAV/35.0.0.48.273;FBDM/{density=1.33125,width=800,height=1205};FBLC/en_US;FBCR/;FBPN/com.facebook.katana;FBDV/Nexus 7;FBSV/4.1.1;FBBK/0;]'
    }
    try:
        response = requests.post(url, data=params, headers=headers, proxies=proxy) if post else requests.get(url, params=params, headers=headers, proxies=proxy)
        return response.json()
    except Exception as e:
        print(f'[×] Error connecting to Facebook API: {e}')
        return {}

def load_proxies():
    """Loads proxies from proxies.txt file."""
    try:
        with open('proxies.txt', 'r') as file:
            proxies = [line.strip() for line in file]
        return [{'http': f'http://{proxy}'} for proxy in proxies]
    except FileNotFoundError:
        print('[×] No proxy file found. Running without proxies.')
        return []

def get_working_proxies():
    """Returns available proxies."""
    return load_proxies()

working_proxies = get_working_proxies()

if not working_proxies:
    print('[×] No working proxies found. Please check your proxies.')
else:
    for i in range(int(input('[+] How Many Accounts You Want:  '))):
        proxy = random.choice(working_proxies)
        email, password, first_name, last_name, birthday = create_1secmail_account()
        if email and password and first_name and last_name and birthday:
            register_facebook_account(email, password, first_name, last_name, birthday, proxy)

print('\x1b[38;5;208m⇼'*60)
