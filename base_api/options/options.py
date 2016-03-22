"""
Options
:description:
Store application option in database.
Get application option from database.
"""


from MySQLdb import IntegrityError
import base_common.msg
from base_common.dbacommon import params
from base_common.dbacommon import authenticated_call
from base_common.dbacommon import app_api_method
from base_common.dbacommon import get_db
from base_lookup import api_messages as msgs
from base_config.service import log

name = "Options"
location = "option"
request_timeout = 10


def _key_exists(db, _key):

    dbc = db.cursor()
    q = '''SELECT * FROM options WHERE o_key = '{}' '''.format(_key)

    try:
        dbc.execute(q)
    except IntegrityError as e:
        log.critical('Error getting option {} from database: {}'.format(_key, e))
        return False    # consider this

    return dbc.rowcount != 0


@authenticated_call()
@app_api_method(
    method='PUT',
    api_return=[(204, ''), (404, '')],
    uri='set'
)
@params(
    {'arg': 'option_name', 'type': str, 'required': True, 'description': 'Key'},
    {'arg': 'option_value', 'type': str, 'required': True, 'description': 'Value'},
)
def set_option(option_name, option_value, **kwargs):
    """
    Set option in database
    """

    _db = get_db()
    dbc = _db.cursor()

    q = '''INSERT into options (o_key, o_value) VALUES ('{}', '{}')'''.format(option_name, option_value)
    _update = False

    if _key_exists(_db, option_name):
        q = '''UPDATE options set o_value = '{}' where o_key = '{}' '''.format(option_value, option_name)
        _update = True

    try:
        dbc.execute(q)
    except IntegrityError as e:
        log.critical('Error {} option {} with {}: {}'.format(
            'update' if _update else 'insert', option_name, option_value, e))
        return base_common.msg.error(msgs.ERROR_SET_OPTION)

    _db.commit()

    return base_common.msg.put_ok()


@authenticated_call()
@app_api_method(
    method='GET',
    api_return=[(200, 'option from db'), (404, '')],
    uri='get'
)
@params(
    {'arg': 'option_name', 'type': str, 'required': True, 'description': 'Key'},
)
def get_option(option_name, **kwargs):
    """
    Get option from database
    """

    _db = get_db()
    dbc = _db.cursor()

    q = '''SELECT o_value FROM options where o_key = '{}' '''.format(option_name)
    try:
        dbc.execute(q)
    except IntegrityError as e:
        log.critical('Error getting option {}: {}'.format(option_name, e))
        return base_common.msg.error(msgs.ERROR_GET_OPTION)

    if dbc.rowcount != 1:
        log.warning('Found {} options {}'.format(dbc.rowcount, option_name))
        return base_common.msg.error(msgs.OPTION_NOT_EXIST)

    _dbr = dbc.fetchone()
    _dbrk = _dbr['o_value']
    res = {}
    res[option_name] = _dbrk

    return base_common.msg.get_ok(res)


@authenticated_call()
@app_api_method(
    method='DELETE',
    api_return=[(204, ''), (404, '')],
    uri='del'
)
@params(
    {'arg': 'option_name', 'type': str, 'required': True, 'description': 'Key'},
)
def del_option(option_name, **kwargs):
    """
    Delete option from database
    """

    _db = get_db()
    dbc = _db.cursor()

    q = '''DELETE FROM options where o_key = '{}' '''.format(option_name)
    try:
        dbc.execute(q)
    except IntegrityError as e:
        log.critical('Error deleting option {}: {}'.format(option_name, e))
        return base_common.msg.error(msgs.ERROR_GET_OPTION)

    _db.commit()

    return base_common.msg.delete_ok()
