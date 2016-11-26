"""
API hooks, functions that will override default base hooks. Possible hooks are
listed in the 'hooks' list, just uncomment and define function with the same
name as in the 'hooks' list.

Possible hooks:

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
post_login_process(username, password, Auth_user) -> [dict, None]
        - after login processing

"""

hooks = [
    # 'pack_user',
    'check_password_is_valid',
    # 'register_user',
    # 'post_register_process',
    # 'user_exists',
    # 'post_login_process',
]


def check_password_is_valid(password):
    return True
