import os
import jwt
import base.base_redis as redis
import datetime

from base.registry import public_key


def token2user(token):
    try:
        decoded = jwt.decode(token, public_key(), algorithms='RS256')
    except Exception as e:
        # print("DECODE PROBLEM", e)
        return False

    r = redis.Redis()
    active = r.get(decoded['id'])

    # print("decoded",decoded)

    now = int(datetime.datetime.now().timestamp())

    try:

        if active == b'1':

            res = {}

            if 'exp' in decoded and decoded['exp']:
                if now > decoded['exp']:
                    return False

            res['id'] = decoded['id']
            res['id_user'] = decoded['id_user'] if 'id_user' in decoded else None
            res['permissions'] = decoded['permissions'] if 'permissions' in decoded else None

            return res

        else:
            return False
    except Exception as e:
        print("EE",e)

        return False
