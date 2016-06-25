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
    rh1.set_argument('message', message)
    kwargs['request_handler'] = rh1
    res = base_api.mail_api.save_mail.do_put(support_mail, receiver, message, **kwargs)
    if 'http_status' not in res or res['http_status'] != 204:
        log.critical('Error save info message')
        return False

    return True

