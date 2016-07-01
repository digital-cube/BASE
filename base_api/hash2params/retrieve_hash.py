# -*- coding: utf-8 -*-

"""
Get params for id
"""

import json
import datetime
from MySQLdb import IntegrityError
import base_common.msg
from base_lookup import api_messages as msgs
from base_config.service import log
from base_common.dbacommon import get_db
from base_common.dbacommon import params
from base_common.dbacommon import app_api_method

name = "GetHashData"
location = "h2p/get"
request_timeout = 10


def prepare_get_query(h2p):
    """
    Make query for given hash
    """

    q = "SELECT id, last_access, data FROM hash_2_params where hash = '{}'".format(h2p)

    return q


def log_hash_access(db, did, ip):
    dbc = db.cursor()
    n = datetime.datetime.now()
    q = "insert into hash_2_params_historylog (id, id_hash_2_params, ip, log_time ) VALUES (null, {}, '{}', '{}')". \
        format(
            did, ip, str(n)
        )
    try:
        dbc.execute(q)
    except IntegrityError as e:
        log.critical('Save hash access log: {}'.format(e))
        return False

    qh = "update hash_2_params set last_access = '{}' where id = {}".format(n, did)

    try:
        dbc.execute(qh)
    except IntegrityError as e:
        log.critical('Change access hash time: {}'.format(e))
        return False

    db.commit()

    return True


@app_api_method(
    method='GET',
    api_return=[(200, 'OK'), (404, 'Missing argument')]
)
@params(
    {'arg': 'hash', 'type': str, 'required': True, 'description': 'data hash'},
    {'arg': 'access', 'type': bool, 'required': False, 'default': False, 'description': 'access to viewed hash'},
)
def do_get(h, grant_access, **kwargs):
    """
    Get data for given hash
    """

    _db = get_db()
    dbc = _db.cursor()

    get_data_q = prepare_get_query(h)

    try:
        dbc.execute(get_data_q)
    except IntegrityError as e:
        log.critical('Retrieve data for hash: {}'.format(e))
        return base_common.msg.error('Retrieve hash data')

    if dbc.rowcount != 1:
        log.warning('Found {} hashes'.format(dbc.rowcount))
        return base_common.msg.error('No data found for given hash')

    dbd = dbc.fetchone()
    d = dbd['data']
    did = dbd['id']
    d_last_accessed = dbd['last_access']

    if d_last_accessed:
        log.warning('New access to {}'.format(h))

        if not log_hash_access(_db, did, kwargs['r_ip']):
            log.warning("Error save hash access log")

        if not grant_access:
            return base_common.msg.error(msgs.WRONG_OR_EXPIRED_TOKEN)

    try:
        d = json.loads(d)
    except Exception as e:
        log.warning('Load hash data: {}'.format(e))

    if not log_hash_access(_db, did, kwargs['r_ip']):
        log.warning("Error save hash access log")

    return base_common.msg.get_ok(d)
