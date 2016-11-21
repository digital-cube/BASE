"""
Application specific hooks:

check_password_is_valid(password) -> bool:
        - check for password validation
register_user(id_user, username, password, data) -> [dict, str, convertible to string, None]:
        - register user on system
        - populate auth_users and users tables here

"""


def check_password_is_valid(*args, **kwargs):
    return True


def register_user(id_user, username, password, data):

    print('REGISTER', id_user, username, password, data)

    return {'register': 'ok'}

