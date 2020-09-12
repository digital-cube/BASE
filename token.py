import os
import jwt
import base.base_redis as redis
import datetime

from base.registry import public_key


def token2user(token):
    try:
        decoded = jwt.decode(token, public_key(), algorithms='RS256')
    except Exception:
        return False, None, None

    r = redis.Redis()
    active = r.get(decoded['id'])

    now = int(datetime.datetime.now().timestamp())

    try:

        if active == b'1':

            if 'exp' in decoded and decoded['exp']:
                if now > decoded['exp']:
                    return False, None, None

            if 'id_user' in decoded:
                return True, decoded['id_user'], decoded['id']
        else:
            return False, None, None
    except:

        return False, None, None
