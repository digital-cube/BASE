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
pre_login_process(Auth_user) -> [dict, str, None]
        - pre login data processing
        - on error raise PreLoginError
post_login_process(Auth_user) -> [dict, str, None]
        - after login processing
        - on error raise PostLoginError
save_hash(hash_data) -> [dict, str, None]
        - save hash data

"""

import json
from base.application.helpers.exceptions import SaveHash2ParamsException
from base.common.utils import log
from base.common.utils import format_password
from base.common.utils import password_match


def pack_user(user):

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
    if len(password) < 6:
        log.critical('Password {} length {} is lower than minimal of 6'.format(password, len(password)))
        return False
    return True


def register_user(id_user, username, password, data):

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

    import base.common.orm
    AuthUser, _session = base.common.orm.get_orm_model('auth_users')

    _q = _session.query(AuthUser).filter(AuthUser.username == username)
    if _q.count() != 1:
        log.warning('User {} not found'.format(username))
        return None

    return _q.one()


def check_username_and_password(username, password, user):

    if not password_match(username, password, user.password):
        log.critical('User {} enters a wrong password: {}'.format(username, password))
        return False

    return True

# END OF THE LOGIN USER PROCESS


# HASH_2_PARAMS

def save_hash(hash_data):

    # import base.config.application_config
    import base.common.orm
    # Hash2Params= base.config.application_config.orm_models['hash_2_params']
    # _session = base.common.orm.orm.session()

    Hash2Params, _session = base.common.orm.get_orm_model('hash_2_params')

    from base.common.sequencer import sequencer
    _hash = sequencer().new('h')

    if not _hash:
        log.critical('Error getting new hash')
        raise SaveHash2ParamsException('Error get new hash for data')

    hash_data = json.dumps(hash_data)
    h2p = Hash2Params(_hash, hash_data)

    _session.add(h2p)
    _session.commit()

    return {'h2p': _hash}

