"""
Save id for params
"""

import datetime
import json
from MySQLdb import IntegrityError

import base_common.msg
from base_config.service import log
from base_common.dbacommon import params
from base_common.dbacommon import app_api_method
from base_common.dbacommon import get_db
from base_common.seq import sequencer
import base_lookup.api_messages as msgs

name = "SaveHash"
location = "h2p/save"
request_timeout = 10


def prepare_hash2params_query(h_id, data):
    """
    Prepare query for insert data into hash_2_params
    """

    n = datetime.datetime.now()
    q = "INSERT INTO hash_2_params (id, hash, time_created, data) " \
        "VALUES (null, '{}', '{}', '{}')".format(
            h_id,
            str(n),
            data
        )

    return q


@app_api_method(
    method='PUT',
    api_return=[(202, 'Data hash'), (404, 'Missing argument')]
)
@params(
    {'arg': 'data', 'type': json, 'required': True, 'description': 'data for storing'},
)
def do_put(hdata, **kwargs):
    """
    Save hash for give parameters
    """

    _db = get_db()
    dbc = _db.cursor()

    h_id = sequencer().new('h')

    h2p = prepare_hash2params_query(h_id, hdata)
    try:
        dbc.execute(h2p)
    except IntegrityError as e:
        log.critical('Insert hash for data: {}'.format(e))
        return base_common.msg.error(msgs.ERROR_SAVE_HASH)

    _db.commit()

    return base_common.msg.post_ok({'h': h_id})

