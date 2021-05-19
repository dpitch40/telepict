import os
import os.path
import secrets 

from telepict.config import Config

code_length = 32

def generate_access_code():
    return secrets.token_urlsafe(code_length)

if __name__ == '__main__':
    d = os.path.abspath(os.path.dirname(Config.ACCESS_CODE_FILE))
    if not os.path.isdir(d):
        os.makedirs(d)
    code = generate_access_code()
    with open(Config.ACCESS_CODE_FILE, 'w') as fobj:
        fobj.write(code + '\n')
    print(f'Generated access code at {Config.ACCESS_CODE_FILE}: {code!r}')
