import jwt
import datetime
from typing import Union
import tortoise.timezone

from .store import Store
from base.src.base.registry import public_key


def token2user(token) -> Union[dict, bool]:
    """
    Function which contacts the Store for user info after it has decoded the token info from the JWT Token
    :param token: JWT Token which needs to be decoded
    :return: Dictionary with user info on success or False on error or Exception raised
    """

    try:
        decoded = jwt.decode(token, public_key(), algorithms='RS256')
    except Exception as e:
        return False

    active = Store.get(decoded['id'])

    # now = int(datetime.datetime.now().timestamp())
    now = int(tortoise.timezone.now().timestamp())

    try:

        if active == True or active in (b'1', b'{"active": true}'):

            res = {}

            if 'expires' in decoded and decoded['expires']:
                if now > decoded['expires']:
                    return False

            res['id'] = decoded['id']
            res['id_user'] = decoded['id_user'] if 'id_user' in decoded else None
            res['permissions'] = decoded['permissions'] if 'permissions' in decoded else None
            res['id_tenant'] = decoded['id_tenant'] if 'id_tenant' in decoded else None

            return res

        else:
            return False
    except Exception as e:
        print("EE", e)

        return False
