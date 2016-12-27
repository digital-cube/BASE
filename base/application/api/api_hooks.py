"""
Application specific hooks:

pack_user(AuthUser) -> [dict, None]:
        - return users data as dictionary
check_password_is_valid(password) -> bool:
        - check for password validation
register_user(id_user, username, password, data) -> [dict, str, convertible to string, None]:
        - register user on system
        - populate auth_users and users tables here
post_register_process(id_user, username, password, data) -> [dict, None]:
        - process user's data after user registration
user_exists(username) -> [User object]
        - check if username exists in the system
check_username_and_password(username, password, Auth_user) -> [bool]
        - check username / password match
pre_login_process(Auth_user, json_data) -> [dict, str, None]
        - pre login data processing
        - on error raise PreLoginError
post_login_process(Auth_user, json_data) -> [dict, str, None]
        - after login processing
        - on error raise PostLoginError
save_hash(hash_data) -> [dict, str]
        - save hash data
get_hash_data(hash) -> [dict, None]
        - retrieve data from hash
save_mail_queue(sender, sender_name, receiver, receiver_name, subject, message, data, get_data) -> [dict, None]
        - save mail queue
pre_logout_process() -> [dict, None]
        - pre logout data processing
post_logout_process() -> [dict, None]
        - post logout data processing
"""

import json
import datetime
from base.application.helpers.exceptions import SaveHash2ParamsException
from base.common.utils import log
from base.common.utils import format_password
from base.common.utils import password_match

def pre_register_user(username):
    return True

def pack_user(user):
    """
    Prepare user's data
    :param user: orm Auth_user
    :return: dict with user's data
    """
    _user = {}
    _user['id'] = user.id
    _user['username'] = user.username

    import base.common.orm
    User, _session = base.common.orm.get_orm_model('users')

    _q = _session.query(User).filter(User.id == user.id)

    if _q.count() == 1:
        _db_user = _q.one()

        _user['first_name'] = _db_user.first_name
        _user['last_name'] = _db_user.last_name
        _user['data'] = _db_user.data

    return _user


# REGISTER USER PROCESS
def check_password_is_valid(password):
    """
    Check if provided password is valid
    :param password: user's password
    :return: bool valid
    """
    if len(password) < 6:
        log.critical('Password {} length {} is lower than minimal of 6'.format(password, len(password)))
        return False
    return True


def register_user(id_user, username, password, data):
    """
    Save user into database
    :param id_user: database user id
    :param username: user's username
    :param password: user's password
    :param data: user's data
    :return: bool success
    """
    import base.common.orm
    AuthUser, _session = base.common.orm.get_orm_model('auth_users')
    User, _ = base.common.orm.get_orm_model('users')

    password = format_password(username, password)

    import base.application.lookup.user_roles as user_roles
    role_flags = int(data['role_flags']) if 'role_flags' in data else user_roles.USER

    _auth_user = AuthUser(id_user, username, password, role_flags, True)
    _session.add(_auth_user)
    _session.commit()

    first_name = data['first_name'] if 'first_name' in data else None
    last_name = data['last_name'] if 'last_name' in data else None
    _data = json.dumps(data)
    _user = User(id_user, first_name, last_name, _data)
    _session.add(_user)
    _session.commit()

    return True


# END OF THE REGISTER USER PROCESS


# LOGIN USER PROCESS
def user_exists(username):
    """
    Check if username is already taken/used
    :param username: user's username
    :return: bool used
    """
    import base.common.orm
    AuthUser, _session = base.common.orm.get_orm_model('auth_users')

    _q = _session.query(AuthUser).filter(AuthUser.username == username)
    if _q.count() != 1:
        log.warning('User {} not found'.format(username))
        return None

    return _q.one()


def check_username_and_password(username, password, user):
    """
    Check username and password for correctness
    :param username: user's username
    :param password: user's password
    :param user: orm Auth_user
    :return: bool correct
    """
    if not password_match(username, password, user.password):
        log.critical('User {} enters a wrong password: {}'.format(username, password))
        return False

    return True


# END OF THE LOGIN USER PROCESS


# HASH_2_PARAMS

def save_hash(hash_data):
    """
    Save hash and corresponding data to database
    :param hash_data: data to be saved with new hash
    :return: hash
    """
    import base.common.orm
    Hash2Params, _session = base.common.orm.get_orm_model('hash_2_params')
    Hash2ParamsHistory, _session = base.common.orm.get_orm_model('hash_2_params_history_log')

    from base.common.sequencer import sequencer
    _hash = sequencer().new('h')

    if not _hash:
        log.critical('Error getting new hash')
        raise SaveHash2ParamsException('Error get new hash for data')

    hash_data = json.dumps(hash_data)
    h2p = Hash2Params(_hash, hash_data)

    _session.add(h2p)
    _session.commit()

    h2p_history = Hash2ParamsHistory(h2p.id, '{}')
    _session.add(h2p_history)
    _session.commit()

    return {'h2p': _hash}


def get_hash_data(h2p):
    """
    Retrieve data for give hash
    :param h2p: hash to find data for
    :return: dict
    """
    import base.common.orm
    Hash2Params, _session = base.common.orm.get_orm_model('hash_2_params')
    Hash2ParamsHistory, _session = base.common.orm.get_orm_model('hash_2_params_history_log')

    _q = _session.query(Hash2Params).filter(Hash2Params.hash == h2p)
    if _q.count() == 0:
        log.warning('Data for hash {} not found'.format(h2p))
        return {}

    res = {}

    db_h2p = _q.one()
    _res = db_h2p.data
    try:
        res = json.loads(_res)
    except json.JSONDecodeError as e:
        log.warning('Error loading hash {} data {}: {}'.format(h2p, _res, e))

    db_h2p.set_last_access(datetime.datetime.now())

    h2p_history = Hash2ParamsHistory(db_h2p.id, '{}')
    _session.add(h2p_history)

    _session.commit()

    return res


# END OF HASH_2_PARAMS

# E-MAIL QUEUE

def save_mail_queue(sender, sender_name, receiver, receiver_name, subject, message, data):
    """
    Save mail to database
    :param sender: email address of the sender
    :param sender_name: display name of the sender
    :param receiver:  email address of the receiver
    :param receiver_name: display name of the receiver
    :param subject: subject of the message
    :param message: body of the message
    :param data: additional message data in json form
    :param get_data: weather to retrieve data in response
    :return: None, dict
    """

    import base.common.orm
    MailQueue, _session = base.common.orm.get_orm_model('mail_queue')

    data = json.dumps(data) if data else data
    mail_queue = MailQueue(sender, sender_name, receiver, receiver_name, subject, message, data)
    _session.add(mail_queue)
    _session.commit()

    return mail_queue.id
