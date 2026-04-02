import urllib.request
import json
import ssl
import re
import binascii
from Crypto.Cipher import AES

def _decrypt(encrypted_hex, key_hex, iv_hex):
    encrypted_bytes = binascii.unhexlify(encrypted_hex)
    key_bytes = binascii.unhexlify(key_hex)
    iv_bytes = binascii.unhexlify(iv_hex)
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    return binascii.hexlify(decrypted_bytes).decode()

def check(url):
    context = ssl._create_unverified_context()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        req1 = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req1, context=context, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        a = re.search(r'var a=toNumbers\("([a-fA-F0-9]+)"\)', html)
        b = re.search(r'b=toNumbers\("([a-fA-F0-9]+)"\)', html)
        c = re.search(r'c=toNumbers\("([a-fA-F0-9]+)"\)', html)
        redirect = re.search(r'location\.href="([^"]+)"', html)
        if not (a and b and c and redirect):
            return None
        cookie_value = _decrypt(c.group(1), a.group(1), b.group(1))
        req2 = urllib.request.Request(redirect.group(1), headers=headers)
        req2.add_header('Cookie', f"__test={cookie_value}")
        with urllib.request.urlopen(req2, context=context, timeout=10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result
    except:
        return None
