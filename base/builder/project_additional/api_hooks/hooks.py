# coding: utf-8
"""
API hooks, functions that will override default base hooks. Possible hooks are
listed in the 'hooks' list, just uncomment and define function with the same
name as in the 'hooks' list.

Possible hooks:

pack_user(AuthUser) -> [dict, None]:
        - return users data as dictionary
check_password_is_valid(password) -> bool:
        - check for password validation
register_user(id_user, username, password, data, request_handler=None) -> [dict, str, convertible to string, None]:
        - register user on system
        - populate auth_users and users tables here
pre_register_user(username, password, data, request_handler=None) -> [False, not False]:
        - process user's data before user registration. If False registration is stopped.
post_register_process(id_user, username, password, data, session_token, request_handler=None) -> [dict, None, bool]:
        - process user's data after user registration. If False or None, registration return error.
user_exists(username, password, data, handler) -> [User object]
        - check if username exists in the system
check_username_and_password(username, password, Auth_user) -> [bool]
        - check username / password match
pre_login_process(Auth_user, json_data, request_handler=None) -> [dict, str, None]
        - pre login data processing
        - on error raise PreLoginError
post_login_process(Auth_user, json_data, token, request_handler=None) -> [dict, str, None]
        - after login processing
        - on error raise PostLoginError
save_hash(hash_data) -> [dict, str]
        - save hash data
get_hash_data(hash) -> [dict, None]
        - retrieve data from hash
save_mail_queue(sender, sender_name, receiver, receiver_name, subject, message, data, get_data, sent=True) -> [dict, None]
        - save mail queue
send_mail_from_queue(sender, sender_name, receiver, receiver_name, subject, message, data, id_mail_queue) -> [dict, bool]
        - send mail
update_mail_status(id_mail_queue, sent_mail_response) -> [bool]
        - update mail in the database
pre_logout_process(Auth_user) -> [dict, None]
        - pre logout data processing
post_logout_process(Auth_user, session_token) -> [dict, None]
        - post logout data processing
check_user(Auth_user, request_handler=None) -> [dict]
        - check user process
pre_check_user(Auth_user) -> [dict]
        - process user before check user process
        - on exception should rise PreCheckUserError
post_check_user(Auth_user) -> [dict]
        - process user after check user process
        - on exception should rise PostCheckUserError
get_mail_from_queue(id_message) -> [dict]
        - get mail data
forgot_password(AuthUser, data) -> [bool]
        - save forgot password request and message
class Tokenizer
        - tokenizer prototype
class SqlTokenizer
        - tokenizer for sql token storage
class RedisTokenizer
        - tokenizer for redis token storage
post_social_login_process(id_user, social_user_data) -> [dict, bool]
get_google_authorized_client_id(auth_data) -> str
        - return google client id based on provided data
"""

hooks = [
    # 'pack_user',
    'check_password_is_valid',
    # 'register_user',
    # 'pre_register_user',
    # 'post_register_process',
    # 'user_exists',
    # 'pre_login_process',
    # 'post_login_process',
    # 'save_hash',
    # 'get_hash_data',
    # 'save_mail_queue',
    # 'send_mail_from_queue',
    # 'update_mail_status',
    # 'pre_logout_process',
    # 'post_logout_process',
    # 'check_user',
    # 'get_mail_from_queue',
    # 'forgot_password',
    # 'post_social_login_process',
    # 'get_google_authorized_client_id',
    # 'Tokenizer',
    # 'SqlTokenizer',
    # 'RedisTokenizer',
]


def check_password_is_valid(password):
    return True


# # This post login hook allows cookie setup for websites that requires cookies (for authentication maybe)
# def post_login_process(Auth_user, json_data, token, request_handler):
#
#     request_handler.set_secure_cookie('token', token['token'])
#     return
