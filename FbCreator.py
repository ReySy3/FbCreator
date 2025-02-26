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
> › Github :- @jatintiwari0 
> › By      :- JATIN TIWARI
> › Proxy Support Added by @coopers-lab
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛                """)
print('\x1b[38;5;208m⇼'*60)
print('\x1b[38;5;22m•'*60)
print('\x1b[38;5;22m•'*60)
print('\x1b[38;5;208m⇼'*60)

def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

def get_mail_domains(proxy=None):
    url = "https://api.mail.tm/domains"
    try:
        response = requests.get(url, proxies=proxy)
        if response.status_code == 200:
            return response.json().get('hydra:member', [])
        else:
            print(f'[×] Email Error: {response.text}')
            return []
    except Exception as e:
        print(f'[×] Error: {e}')
        return []

def create_mail_tm_account(proxy=None):
    fake = Faker()
    mail_domains = get_mail_domains(proxy)
    if not mail_domains:
        return None, None, None, None, None

    domain = random.choice(mail_domains)['domain']
    username = generate_random_string(10)
    password = fake.password()
    birthday = fake.date_of_birth(minimum_age=18, maximum_age=45)
    first_name = fake.first_name()
    last_name = fake.last_name()
    url = "https://api.mail.tm/accounts"
    headers = {"Content-Type": "application/json"}
    data = {"address": f"{username}@{domain}", "password": password}       

    try:
        response = requests.post(url, headers=headers, json=data, proxies=proxy)
        if response.status_code == 201:
            return f"{username}@{domain}", password, first_name, last_name, birthday
        else:
            print(f'[×] Email Creation Error: {response.text}')
            return None, None, None, None, None
    except Exception as e:
        print(f'[×] Error: {e}')
        return None, None, None, None, None

def get_verification_code(email, password, proxy=None):
    """Fetches the verification code from the email inbox."""
    auth_url = "https://api.mail.tm/token"
    auth_data = {"address": email, "password": password}

    try:
        auth_response = requests.post(auth_url, json=auth_data, proxies=proxy)
        if auth_response.status_code != 200:
            print("[×] Failed to authenticate with mail.tm")
            return None
        
        token = auth_response.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}

        inbox_url = "https://api.mail.tm/messages"
        for _ in range(10):  # Try for 10 seconds
            inbox_response = requests.get(inbox_url, headers=headers, proxies=proxy)
            if inbox_response.status_code == 200:
                messages = inbox_response.json().get("hydra:member", [])
                if messages:
                    latest_email_id = messages[0]["id"]
                    message_url = f"https://api.mail.tm/messages/{latest_email_id}"
                    message_response = requests.get(message_url, headers=headers, proxies=proxy)
                    if message_response.status_code == 200:
                        content = message_response.json().get("text", "")
                        code_match = re.search(r'\b\d{6}\b', content)  # Assuming a 6-digit code
                        if code_match:
                            return code_match.group()
            time.sleep(2)
    except Exception as e:
        print(f"[×] Error fetching email: {e}")
    
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

    verification_code = get_verification_code(email, password, proxy)

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
    headers = {'User-Agent': '[FBAN/FB4A;FBAV/35.0.0.48.273;FBDM/{density=1.33125,width=800,height=1205};FBLC/en_US;FBCR/;FBPN/com.facebook.katana;FBDV/Nexus 7;FBSV/4.1.1;FBBK/0;]'}
    if post:
        response = requests.post(url, data=params, headers=headers, proxies=proxy)
    else:
        response = requests.get(url, params=params, headers=headers, proxies=proxy)
    return response.json()

def load_proxies():
    with open('proxies.txt', 'r') as file:
        proxies = [line.strip() for line in file]
    return [{'http': f'http://{proxy}'} for proxy in proxies]

def get_working_proxies():
    proxies = load_proxies()
    return proxies if proxies else []

working_proxies = get_working_proxies()

if not working_proxies:
    print('[×] No working proxies found. Please check your proxies.')
else:
    for i in range(int(input('[+] How Many Accounts You Want:  '))):
        proxy = random.choice(working_proxies)
        email, password, first_name, last_name, birthday = create_mail_tm_account(proxy)
        if email and password and first_name and last_name and birthday:
            register_facebook_account(email, password, first_name, last_name, birthday, proxy)

print('\x1b[38;5;208m⇼'*60)
