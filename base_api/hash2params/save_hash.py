"""
Save id for params
"""

import datetime
import json
from MySQLdb import IntegrityError

import base_common.msg
from base_common.dbacommon import params
from base_common.dbacommon import app_api_method
from base_common.dbacommon import get_db
from base_common.seq import sequencer

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


@app_api_method
@params(
    {'arg': 'data', 'type': json, 'required': True},
)
def do_put(request, *args, **kwargs):
    """
    Save hash for give parameters
    :param hash_data: data for storing, string, True
    :return:  202, Data hash
    :return:  404, Missing argument
    """

    log = request.log

    _db = get_db()
    dbc = _db.cursor()

    hdata, = args

    h_id = sequencer().new('h')

    h2p = prepare_hash2params_query(h_id, hdata)
    try:
        dbc.execute(h2p)
    except IntegrityError as e:
        log.critical('Insert hash for data: {}'.format(e))
        return base_common.msg.error('Save data hash')

    _db.commit()

    return base_common.msg.post_ok({'h': h_id})

