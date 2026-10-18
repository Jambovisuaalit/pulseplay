"""Create local credentials without putting passwords in shell history or logs."""
import getpass
import hashlib
import os
import secrets
from pathlib import Path

path = Path(__file__).resolve().parents[1] / '.env.local'
username = input('Operator username: ').strip()
password = getpass.getpass('Password (minimum 24 characters): ')
if not username or len(username) > 128 or not 24 <= len(password) <= 256:
    raise SystemExit('Invalid username or password length')
if password != getpass.getpass('Repeat password: '):
    raise SystemExit('Passwords do not match')
salt = secrets.token_hex(16)
derived = hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1, dklen=64).hex()
# Exclusive creation prevents accidental replacement of existing project secrets.
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'w') as handle:
    import json
    handle.write('TP_AUTH_USERNAME=' + json.dumps(username) + '\n')
    handle.write('TP_AUTH_PASSWORD_SCRYPT=' + salt + ':' + derived + '\n')
    handle.write('TP_SESSION_SECRET=' + secrets.token_hex(32) + '\n')
print('Created .env.local with owner-only permissions. No values printed.')
