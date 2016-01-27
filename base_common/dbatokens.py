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


def __get_user_by_token(dbc, tk, log):

    q = "select id, id_user, created, closed from session_token where id = '{}'".format(qu_esc(tk))

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


def authorized_by_token(dbc, tk, log):

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


def get_user_by_token(dbc, tk, log):

    if not __get_user_by_token(dbc, tk, log):
        log.critical('Cannot find users token')
        return False

    db_tk = dbc.fetchone()
    u_id = db_tk['id_user']

    q = "select username, password from users where id = '{}'".format(u_id)

    try:
        dbc.execute(q)
    except Exception as e:
        log.critical('Error find user by token')
        return False

    if dbc.rowcount != 1:
        log.warning('Fount {} users with id {}'.format(dbc.rowcount, u_id))
    user = dbc.fetchone()
    username = user['username']
    password = user['password']

    return (username, password)
