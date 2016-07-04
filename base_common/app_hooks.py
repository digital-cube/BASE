# -*- coding: utf-8 -*-

"""
Application specific hooks will be added to this module, or
existing will be overloaded if needed
check_password_is_valid -- validate given password (parameters: password) (user_register)
post_register_digest -- post register users data processing
                        (parameters: users id, username, password, json users data) (user_register)
prepare_user_query -- prepare query for insert user in db
                        (parameters: request handler, users id, username, password, json users data) (user_register)
pack_user_by_id -- get user from db by it's id (db connection, user id) (dbtokens)
prepare_login_query -- prepare query for user login (parameters: username)
post_login_digest -- post login processing (parameters: id_user, username, password(plain), login token)
change_username_hook -- change username modifications (parameters: hash for hash_2_param, new username, dbuser, **kwargs)
change_username_success_hook -- change username modifications (parameters: )
forgot_password_hook - forgot password (parameters: )
"""

import base_config.settings
from base_common.dbacommon import format_password
from base_config.service import log
from base_config.service import support_mail
from base_svc.comm import BaseAPIRequestHandler
import base_api.mail_api.save_mail


def prepare_user_query(u_id, username, password, *args, **kwargs):
    """
    User registration query
    :param u_id:  user's id (unique)
    :param username:  user's username
    :param password:  given password
    :param args:  additional arguments (application specific)
    :param kwargs:  additional named arguments (application specific)
    :return:
    """

    password = format_password(username, password)

    # role_flags - HARDCODED to 1

    q = "INSERT into users (id, username, password, role_flags, active) VALUES " \
        "('{}', '{}', '{}', 1, true)".format(
                u_id,
                username,
                password)

    return q


def pack_user_by_id(db, id_user, get_dict=False):
    """
    Pack users information in DBUser class instance
    :param db: database
    :param id_user: users id
    :param get_dict: export user like DBUser or dict
    :return: DBUser instance or user dict
    """

    dbc = db.cursor()
    q = "select id, username, password, role_flags, active from users where id = '{}'".format(id_user)

    import MySQLdb
    try:
        dbc.execute(q)
    except MySQLdb.IntegrityError as e:
        log.critical('Error find user by token: {}'.format(e))
        return False

    if dbc.rowcount != 1:
        log.critical('Fount {} users with id {}'.format(dbc.rowcount, id_user))
        return False

    #DUMMY CLASS INSTANCE USER JUST FOR EASIER MANIPULATION OF DATA
    class DBUser:

        def dump_user(self):
            ret = {}
            for k in self.__dict__:
                if self.__dict__[k]:
                    ret[k] = self.__dict__[k]

            return ret

    db_user = DBUser()

    user = dbc.fetchone()
    db_user.id_user = user['id']
    db_user.username = user['username']
    db_user.password = user['password']
    db_user.role = user['role_flags']
    db_user.active = user['active']

    return db_user.dump_user() if get_dict else db_user


def prepare_login_query(username):

    q = "select id, password from users where username = '{}' and active=1".format( username )

    return q

password_change_uri = 'user/password/new'

def get_email_message(request, username, tk):

    m = """Dear {},<br/> follow the link bellow to change your password:<br/>http://{}/{}/{}""".format(
            username,
            request.request.host,
            password_change_uri,
            tk)

    return m

def _get_email_warning(oldusername, newusername):
    """
    Create warning email for old username
    :param request:  request handler
    :param oldusername:  old username
    :param newusername:  new username
    :param h:  hash
    :return:  message as string
    """
    m = '''Dear,<br/>we have receive request for changing username {} to {}.<br/> If You request the change take no
    further actions.<br/>If this action is not performed by You please contact our support at {}.
    Thank you for using our services.'''.format(oldusername, newusername, support_mail)

    return m


def _get_email_message(h):
    """
    Create email message
    :param request:  request handler
    :param oldusername:  old username
    :param newusername:  new username
    :param h:  hash for change
    :return:  message text as string
    """

    l = '{}/{}'.format(base_config.settings.CHANGE_EMAIL_ADDRESS, h)
    m = '''Dear,<br/>You have requested username change. Please confirm change by following the link below:<br/>
    {}<br/><br/>If You didn't requested the change, please ignore this message.<br/>Thank You!'''.format(l)

    return m


def change_username_hook(hash2param, newusername, dbuser, **kwargs):

        # jedan hook za oba mail-a
    message = _get_email_message(hash2param)

    # SAVE EMAILS FOR SENDING
    rh1 = BaseAPIRequestHandler()
    rh1.set_argument('sender', support_mail)
    rh1.set_argument('receiver', newusername)
    rh1.set_argument('subject', 'Username change request')
    rh1.set_argument('message', message)
    kwargs['request_handler'] = rh1
    res = base_api.mail_api.save_mail.do_put(support_mail, newusername, message, **kwargs)
    if 'http_status' not in res or res['http_status'] != 204:
        log.critical('Error save redirection email')
        return False

    message2 = _get_email_warning(dbuser.username, newusername)

    rh2 = BaseAPIRequestHandler()
    rh2.set_argument('sender', support_mail)
    rh2.set_argument('receiver', dbuser.username)
    rh2.set_argument('subject', 'Username change request saved')
    rh2.set_argument('message', message2)
    kwargs['request_handler'] = rh2
    res = base_api.mail_api.save_mail.do_put(support_mail, dbuser.username, message2, **kwargs)
    if 'http_status' not in res or res['http_status'] != 204:
        log.critical('Error save warning email')
        return False

    return True


def change_username_success_hook(receiver, **kwargs):

    message = 'Dear,<br/> Your username has been updated!<br/>Thank You!'

    # SAVE EMAILS FOR SENDING
    rh1 = BaseAPIRequestHandler()
    rh1.set_argument('sender', support_mail)
    rh1.set_argument('receiver', receiver)
    rh1.set_argument('subject', 'Username successfully changed')
    rh1.set_argument('message', message)
    kwargs['request_handler'] = rh1
    res = base_api.mail_api.save_mail.do_put(support_mail, receiver, message, **kwargs)
    if 'http_status' not in res or res['http_status'] != 204:
        log.critical('Error save info message')
        return False

    return True

def forgot_password_hook(request, receiver, tk, **kwargs):

    message = get_email_message(request, receiver, tk)

    # SAVE EMAILS FOR SENDING
    rh1 = BaseAPIRequestHandler()
    rh1.set_argument('sender', support_mail)
    rh1.set_argument('receiver', receiver)
    rh1.set_argument('subject', 'Forgot password query')
    rh1.set_argument('message', message)
    kwargs['request_handler'] = rh1
    res = base_api.mail_api.save_mail.do_put(support_mail, receiver, message, **kwargs)
    if 'http_status' not in res or res['http_status'] != 204:
        log.critical('Error save info message')
        return False

    return True


def check_password_is_valid(password, *args, **kwargs):

    import re

    server_msg = None

    _password = password
    password = _password.lower()
    # _first_name = first_name.lower()
    # _last_name = last_name.lower()
    # _email = username.lower()

    # email_uname = _email.split('@')[0]
    # email_domain = _email.split('@')[1]

    if len(password) < 8:
        server_msg = "Minimum password length should be 8 characters"
        log.critical(server_msg)
        return False, server_msg

    if not (re.compile(r'.*[a-z]')).match(_password):
        server_msg = "Password should contain at least one lowercase character"
        log.critical(server_msg)
        return False, server_msg

    if not (re.compile(r'.*[A-Z]')).match(_password):
        server_msg = "Password should contain at least one uppercase character"
        log.critical(server_msg)
        return False, server_msg

    if not (re.compile(r'.*[0-9]')).match(_password):
        server_msg = "Password should contain at least one number"
        log.critical(server_msg)
        return False, server_msg

    # if (re.compile(".*" + _first_name)).match(password) or (re.compile(".*" + _last_name)).match(password):
    #     log.critical("Password should not contains first or last name :{},{}".format(first_name, last_name))
    #     return False

    # if (re.compile(".*" + email_uname)).match(password) or (re.compile(".*" + email_domain)).match(password):
    #     log.critical("Password should not contains email or domain :{},{}".format(email_uname, email_domain))
    #     return False

    not_allowed = []
    for i in range(1, 8):
        res = str(i) + str(i + 1) + str(i + 2)
        not_allowed.append(res)

    for i in range(9, 2, -1):
        res = str(i) + str(i - 1) + str(i - 2)
        not_allowed.append(res)

    not_allowed.extend(('qwe', 'asd', 'zxc', 'qaz', 'qay', 'abc', 'xyz'))

    for i in range(len(not_allowed) - 1, -1, -1):
        if (re.compile(".*" + not_allowed[i])).match(_password):
            server_msg = "Password should not contain :{}".format(not_allowed[i])
            log.critical(server_msg)
            return False, server_msg

    allowed = r'`!"?$%?^&*()_-={[}]:;@\'~#|\<,>.?/+'

    for i in range(ord('a'), ord('z') + 1):
        allowed += chr(i)

    for i in range(ord('0'), ord('9') + 1):
        allowed += chr(i)

    for i in range(len(password) - 1, -1, -1):
        k = password[i]
        for j in range(0, len(allowed)):
            if k not in allowed:
                server_msg = "Password should not contain :{}".format(k)
                log.critical(server_msg)
                return False, server_msg

    return True, 'ok'
