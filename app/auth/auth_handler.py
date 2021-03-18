import time
from typing import Dict

import jwt
from decouple import config
from main import r


JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


def signJWT(user_id: int, role: str):
    payload = {
        "id": user_id,
        "role": role
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    r.set(token, user_id)
    return token


def decodeJWT(token: str):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token
    except:
        return {}
