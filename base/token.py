import os
import jwt
import redis
import datetime

current_file_folder = os.path.dirname(os.path.realpath(__file__))
with open(current_file_folder + '/../config/id_rsa.pub', 'rb') as f:
    public_key = f.read()


def token2user(token):

    try:
        decoded = jwt.decode(token, public_key, algorithms='RS256')
    except:
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
