"""
Application specific hooks:

check_password_is_valid(password) -> bool:
        - check for password validation
register_user(id_user, username, password, data) -> [dict, str, convertible to string, None]:
        - register user on system
        - populate auth_users and users tables here
post_register_process(id_user, username, password, data) -> [dict, None]:
        - process user's data after user registration

"""

import json
from base.common.utils import log
from base.common.utils import format_password


def check_password_is_valid(password):
    if len(password) < 6:
        log.critical('Password {} length {} is lower than minimal of 6'.format(password, len(password)))
        return False
    return True


def register_user(id_user, username, password, data):

    import base.config.application_config
    import base.common.orm
    AuthUsers = base.config.application_config.orm_models['auth_users']
    User = base.config.application_config.orm_models['users']
    _session = base.common.orm.orm.session()

    password = format_password(username, password)

    print('REGISTER', id_user, username, password, data)
    _auth_user = AuthUsers(id_user, username, password)
    _session.add(_auth_user)
    _session.commit()

    first_name = data['first_name'] if 'first_name' in data else None
    last_name = data['last_name'] if 'last_name' in data else None
    _data = json.dumps(data)
    _user = User(id_user, first_name, last_name, _data)
    _session.add(_user)
    _session.commit()

    return True

