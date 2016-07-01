# -*- coding: utf-8 -*-

import json
import datetime
import base_common.app_hooks
from base_common.dbaexc import ErrorSetSessionToken
from base_common.seq import sequencer
from base_config.service import log
from base_common.dbacommon import get_redis_db
from base_config.settings import SESSION_STORAGE
from base_lookup import session_storage as ss


def __get_assigned_token_from_sql(dbc, uid):

    q = "select id from session_token where id_user = '{}' and not closed".format(uid)
    dbc.execute(q)
    if dbc.rowcount != 1:
        return False

    return dbc.fetchone()['id']


def __get_assigned_token_from_redis(uid):

    # ALWAYS CREATE TOKEN IN REDIS
    return False


def __get_assigned_token(dbc, uid):
    if SESSION_STORAGE in ss.map_ and ss.map_[SESSION_STORAGE] == ss.REDIS:
        return __get_assigned_token_from_redis(uid)

    return __get_assigned_token_from_sql(dbc, uid)


def get_token(uid, dbc):

    # RETRIEVE ASSIGNED TOKEN
    __tk = __get_assigned_token(dbc, uid)
    if __tk:
        return __tk

    __tk = sequencer().new('s')

    try:
        __set_session_token(dbc, uid, __tk)
    except ErrorSetSessionToken:
        return None

    return __tk


def __set_session_token(dbc, uid, tk):

    if SESSION_STORAGE in ss.map_ and ss.map_[SESSION_STORAGE] == ss.REDIS:
        __set_session_token_in_redis(uid, tk)
    else:
        __set_session_token_in_sql(dbc, uid, tk)


def __set_session_token_in_redis(uid, tk):

    r = get_redis_db()
    n = datetime.datetime.now()
    n = str(n)[:19]

    _rd = {
        'created': n,
        'id_user': uid
    }
    r.set(tk, json.dumps(_rd, ensure_ascii=False))


def __set_session_token_in_sql(dbc, uid, tk):

    n = datetime.datetime.now()
    n = str(n)[:19]

    q = "INSERT INTO session_token (id, id_user, created) VALUES ('{}', '{}', '{}')".format(
            tk,
            uid,
            n)

    try:
        dbc.execute(q)
    except Exception as e:
        raise ErrorSetSessionToken


def __get_user_by_token_from_redis(tk, is_active):

    r = get_redis_db()
    return r.exists(tk)


def __get_user_by_token_from_sql(dbc, tk, is_active):

    q = '''SELECT
              s.id id, s.id_user id_user, s.created created, s.closed closed
            FROM
              session_token s JOIN users u ON s.id_user = u.id
            WHERE
              s.id = '{}' {} AND NOT s.closed'''.format(
        tk,
        ' AND u.active ' if is_active else ''
        )

    try:
        dbc.execute(q)
    except Exception as e:
        log.critical('Get session: {}'.format(e))
        return False

    if dbc.rowcount != 1:
        log.critical('Found {} sessions'.format(dbc.rowcount))
        return False

    return True


def close_session_by_token(dbc, tk):
    if SESSION_STORAGE in ss.map_ and ss.map_[SESSION_STORAGE] == ss.REDIS:
        return __close_session_by_token_in_redis(tk)

    return __close_session_by_token_in_sql(dbc, tk)


def __close_session_by_token_in_redis(tk):

    r = get_redis_db()
    r.delete(tk)

    return True


def __close_session_by_token_in_sql(dbc, tk):

    q = "update session_token set closed = true where id = '{}'".format(tk)

    try:
        dbc.execute(q)
    except Exception as e:
        log.critical('Close session: {}'.format(e))
        return False

    return True


def authorized_by_token(db, tk):

    if not tk:
        log.warning("Access token not provided")
        return False

    if SESSION_STORAGE in ss.map_ and ss.map_[SESSION_STORAGE] == ss.REDIS:
        return _authorized_by_token_in_redis(tk)

    return _authorized_by_token_in_sql(db, tk)


def _authorized_by_token_in_redis(tk):

    if not __get_user_by_token_from_redis(tk, True):
        log.warning("Access token {} not found".format(tk))
        return False

    return True


def _authorized_by_token_in_sql(db, tk):

    dbc = db.cursor()
    if not __get_user_by_token_from_sql(dbc, tk, True):
        log.warning("Access token {} not found".format(tk))
        return False

    db_u = dbc.fetchone()
    if db_u['closed']:
        log.warning("Session {} closed".format(tk))
        return False

    return True


def get_user_by_token(db, tk, is_active=True):
    if SESSION_STORAGE in ss.map_ and ss.map_[SESSION_STORAGE] == ss.REDIS:
        return _get_user_by_token_from_redis(db, tk, is_active)

    return _get_user_by_token_from_sql(db, tk, is_active)


def _get_user_by_token_from_redis(db, tk, is_active):

    r = get_redis_db()
    _rd = r.get(tk)
    if not _rd:
        log.critical('Cannot find users token {} in redis'.format(tk))
        return False

    import json.decoder
    try:
        _rd = json.loads(_rd.decode('utf-8'))
    except json.decoder.JSONDecodeError as e:
        log.critical('Error loading token {} string {}: {}'.format(tk, _rd, e))
        return False

    u_id = _rd['id_user']

    return base_common.app_hooks.pack_user_by_id(db, u_id)


def _get_user_by_token_from_sql(db, tk, is_active):

    dbc = db.cursor()
    if not __get_user_by_token_from_sql(dbc, tk, is_active):
        log.critical('Cannot find users token {} in sql'.format(tk))
        return False

    db_tk = dbc.fetchone()
    u_id = db_tk['id_user']

    return base_common.app_hooks.pack_user_by_id(db, u_id)


def get_user_by_id(db, id_user):

    return base_common.app_hooks.pack_user_by_id(db, id_user)


