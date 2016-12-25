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

hooks = [
    # 'pack_user',
    'check_password_is_valid',
    # 'register_user',
    # 'post_register_process',
    # 'user_exists',
    # 'pre_login_process',
    # 'post_login_process',
    # 'save_hash',
    # 'get_hash_data',
    # 'save_mail_queue',
    # 'pre_logout_process'
    # 'post_logout_process'
]


def check_password_is_valid(password):
    return True
