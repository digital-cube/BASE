import sys
import time
import base
import json
import psycopg2


def wait4store(max_attempts=30):
    if base.config.conf['store']['type'] == 'redis':
        import redis

        host = base.config.conf['store']['host']
        port = base.config.conf['store']['port']

        for attempt in range(1, max_attempts):
            try:
                r = redis.Redis(host=host,
                                port=port)

            except Exception as e:
                print(f"waiting for redis server {host}:{port}")
                time.sleep(attempt)
                continue
            break
        if attempt == max_attempts - 1:
            print("...error connecting to redis")
            return False

        print("...redis is ready")
        return True
    return True


def wait4store_permissions(max_attempt=30):
    for attempt in range(1, max_attempt):

        if base.store.exists('permissions') == 0:
            print('waiting for user service to setup permissions')
            time.sleep(attempt)
            continue
        if base.store.exists('users_service_public_key') == 0:
            print('waiting for user service to setup public key')
            time.sleep(attempt)
            continue
        break

    if attempt == max_attempt - 1:
        return False
    permissions = base.store.get('permissions')
    permissions = json.loads(permissions)
    print("...users service / permissions is ready; permissions=", permissions)

    return True


def wait4database(db_config, max_attempts=30):
    if db_config['type'] == 'postgres':

        db_user = db_config['user'] if 'user' in db_config else db_config['username']

        for attempt in range(1, max_attempts):
            try:
                c = psycopg2.connect(database=db_config['database'],
                                     user=db_user,
                                     password=db_config['password'],
                                     host=db_config['host'],
                                     port=db_config['port'])
            except:
                c = None

            if c and not c.closed:
                c.close()
                print(f"...database can accept connections {db_config['host']}:{db_config['port']}")
                sys.exit(0)

            print(
                f"waiting for postgres server {db_user}@{db_config['host']}:{db_config['port']}/{db_config['database']} ...")
            time.sleep(attempt)

        return False

    return True
