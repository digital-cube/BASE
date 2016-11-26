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

"""

import json
from base.common.utils import log
from base.common.utils import format_password
from base.common.utils import password_match

def pack_user(user):

    _user = {}
    _user['id'] = user.id
    _user['username'] = user.username

    import base.config.application_config
    import base.common.orm
    User = base.config.application_config.orm_models['users']
    _session = base.common.orm.orm.session()

    _q = _session.query(User).filter(User.id == user.id)

    if _q.count() == 1:
        _db_user = _q.one()

        _user['id'] = user.id

    return _user

# REGISTER USER PROCESS
def check_password_is_valid(password):
    if len(password) < 6:
        log.critical('Password {} length {} is lower than minimal of 6'.format(password, len(password)))
        return False
    return True


def register_user(id_user, username, password, data):

    import base.config.application_config
    import base.common.orm
    AuthUser = base.config.application_config.orm_models['auth_users']
    User = base.config.application_config.orm_models['users']
    _session = base.common.orm.orm.session()

    password = format_password(username, password)
    import src.lookup.user_roles as user_roles
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

    import base.config.application_config
    import base.common.orm
    AuthUser = base.config.application_config.orm_models['auth_users']
    _session = base.common.orm.orm.session()

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

