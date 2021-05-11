import jwt
import json
import datetime
from typing import Union

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

    token_data = Store.get(decoded['id'])

    now = int(datetime.datetime.now().timestamp())

    try:

        token_data = str(token_data, 'utf8')
        token_data = json.loads(token_data)
        if 'active' in token_data and token_data['active']:

            if 'exp' in decoded and decoded['exp']:
                if now > decoded['exp']:
                    return False

            res = {
                'user': token_data
            }
            res['id_session'] = decoded['id']
            res['id_user'] = decoded['id_user'] if 'id_user' in decoded else None
            res['permissions'] = decoded['permissions'] if 'permissions' in decoded else None
            res['id_tenant'] = decoded['id_tenant'] if 'id_tenant' in decoded else None
            res['id_groups'] = decoded['id_groups'] if 'id_groups' in decoded else None

            return res

        else:
            return False
    except Exception as e:
        print("EE", e)

        return False
