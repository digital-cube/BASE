import base_common.app_hooks
from base_common.dbaexc import ErrorSetSessionToken
from base_common.dbacommon import qu_esc
from base_common.seq import sequencer


def __get_assigned_token(dbc,log,uid):

    q = "select id from session_token where id_user = '{}' and not closed".format(qu_esc(uid))
    dbc.execute(q)
    if dbc.rowcount != 1:
        return False

    return dbc.fetchone()['id']


def get_token(uid, dbc, log):

    # RETRIEVE ASSIGNED TOKEN

    __tk = __get_assigned_token(dbc, log, uid)
    if __tk:
        return __tk

    __tk = sequencer().new('s')

    try:
        __set_session_token(dbc, uid, __tk)
    except ErrorSetSessionToken:
        return None

    return __tk


def __set_session_token(dbc, uid, tk):

    import datetime
    n = datetime.datetime.now()
    n = str(n)[:19]

    q = "INSERT INTO session_token (id, id_user, created) VALUES ('{}', '{}', '{}')".format(
            qu_esc(tk),
            qu_esc(uid),
            qu_esc(n))

    try:
        dbc.execute(q)
    except Exception as e:
        raise ErrorSetSessionToken


def __get_user_by_token(dbc, tk, log, is_active=True):

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


def close_session_by_token(dbc, tk, log):

    q = "update session_token set closed = true where id = '{}'".format(qu_esc(tk))

    try:
        dbc.execute(q)
    except Exception as e:
        log.critical('Close session: {}'.format(e))
        return False

    return True


def authorized_by_token(db, tk, log):

    dbc = db.cursor()
    if not tk:
        log.warning("Access token not provided")
        return False

    if not __get_user_by_token(dbc, tk, log):
        log.warning("Access token {} not found".format(tk))
        return False

    db_u = dbc.fetchone()
    if db_u['closed']:
        log.warning("Session {} closed".format(tk))
        return False

    return True


def get_user_by_token(db, tk, log, is_active=True):

    dbc = db.cursor()
    if not __get_user_by_token(dbc, tk, log, is_active):
        log.critical('Cannot find users token')
        return False

    db_tk = dbc.fetchone()
    u_id = db_tk['id_user']

    return base_common.app_hooks.pack_user_by_id(db, u_id, log)


def get_user_by_id(db, user_id, log):

    return base_common.app_hooks.pack_user_by_id(db, user_id, log)


