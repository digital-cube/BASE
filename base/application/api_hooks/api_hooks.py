# coding: utf-8
"""
Application specific hooks:

pack_user(AuthUser) -> [dict, None]:
        - return users data as dictionary
check_password_is_valid(password) -> bool:
        - check for password validation
register_user(id_user, username, password, data, request_handler=None) -> [dict, str, convertible to string, None]:
        - register user on system
        - populate auth_users and users tables here
pre_register_user(username, password, data, request_handler=None) -> [None]:
        - process user's data before user registration
post_register_process(id_user, username, password, data, session_token, request_handler=None) -> [dict, None]:
        - process user's data after user registration
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

import json
import datetime
from functools import reduce
from base.application.helpers.exceptions import SaveHash2ParamsException
from base.common.utils import log
from base.common.utils import format_password
from base.common.utils import password_match

from base.application.api_hooks.token_hooks import Tokenizer
from base.application.api_hooks.token_hooks import SqlTokenizer
from base.application.api_hooks.token_hooks import RedisTokenizer


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
    with base.common.orm.orm_session() as _session:
        User = base.common.orm.get_orm_model('users')

        _q = _session.query(User).filter(User.id == user.id)

        if _q.count() == 1:
            _db_user = _q.one()

            _user['first_name'] = _db_user.first_name
            _user['last_name'] = _db_user.last_name

    return _user


# REGISTER USER PROCESS
def check_password_is_valid(password):
    """
    Check if provided password is valid
    :param password: user's password
    :return: bool valid
    """
    from base.common.utils import log

    if len(password) < 6:
        log.critical('Password {} length {} is lower than minimal of 6'.format(password, len(password)))
        return False
    return True


def register_user(id_user, username, password, data, request_handler=None):
    """
    Save user into database
    :param id_user: database user id
    :param username: user's username
    :param password: user's password
    :param data: user's data
    :return: bool success
    """
    import base.common.orm
    from base.common.utils import log

    AuthUser = base.common.orm.get_orm_model('auth_users')
    User = base.common.orm.get_orm_model('users')

    with base.common.orm.orm_session() as _session:
        password = format_password(username, password)

        import base.application.lookup.user_roles as user_roles
        role_flags = int(data['role_flags']) if 'role_flags' in data else user_roles.USER

        _all_roles = reduce(lambda a, b: a|b, list(user_roles.lmap.keys()))
        if not role_flags & _all_roles:
            log.critical('Wrong role type: {}'.format(role_flags))
            return 'Wrong user role type {}'.format(role_flags)

        _auth_user = AuthUser(id_user, username, password, role_flags, True)
        _session.add(_auth_user)

        first_name = data['first_name'] if 'first_name' in data else None
        last_name = data['last_name'] if 'last_name' in data else None

        _user = User(id_user, first_name, last_name)
        _auth_user.user = _user

        try:
            _session.commit()
        except Exception as e:
            log.critical('Error create user {}: {}'.format(username, e))
            _session.rollback()
            return False
        
        return pack_user(_auth_user)


# END OF THE REGISTER USER PROCESS


# LOGIN USER PROCESS
def user_exists(username, password, data, handler):
    """
    Check if username is already taken/used
    :param username: user's username
    :return: bool used
    """
    import base.common.orm
    AuthUser = base.common.orm.get_orm_model('auth_users')
    with base.common.orm.orm_session() as _session:

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


def check_user(auth_user, request_handler=None):
    """
    Check logged user and return it's data.
    On error raise CheckUserError exception
    :param auth_user:
    :return: dict with user's data
    """

    res = {
        'id': auth_user.id,
        'username': auth_user.username,
        'first_name': auth_user.user.first_name,
        'last_name': auth_user.user.last_name
    }

    return res


# END OF THE LOGIN USER PROCESS


# HASH_2_PARAMS

def save_hash(hash_data):
    """
    Save hash and corresponding data to database
    :param hash_data: data to be saved with new hash
    :return: hash
    """
    import base.common.orm
    Hash2Params = base.common.orm.get_orm_model('hash_2_params')
    Hash2ParamsHistory = base.common.orm.get_orm_model('hash_2_params_history_log')
    with base.common.orm.orm_session() as _session:

        from base.common.sequencer import sequencer
        _hash = sequencer().new('h', session=_session)

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
    Hash2Params = base.common.orm.get_orm_model('hash_2_params')
    Hash2ParamsHistory = base.common.orm.get_orm_model('hash_2_params_history_log')

    with base.common.orm.orm_session() as _session:
        
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

def save_mail_queue(sender, sender_name, receiver, receiver_name, subject, message, data, sent=True):
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
    :param sent: should new mail have status sent or not
    :return: int
    """

    import base.common.orm
    MailQueue = base.common.orm.get_orm_model('mail_queue')
    with base.common.orm.orm_session() as _session:

        data = json.dumps(data) if data else data
        mail_queue = MailQueue(sender, sender_name, receiver, receiver_name, subject, message, data, sent)
        _session.add(mail_queue)
        _session.commit()
        
        return mail_queue.id


def get_mail_from_queue(id_message):
    """
    Get message data from queue table by message id
    :param id_message: id of the message to retrieve
    :return: message data dictionary
    """

    import base.common.orm
    MailQueue = base.common.orm.get_orm_model('mail_queue')
    with base.common.orm.orm_session() as _session:

        q = _session.query(MailQueue).filter(MailQueue.id == id_message)

        res = {}

        if q.count() == 0:
            log.info('No message with id {} found'.format(id_message))
            return False

        msg = q.one()

        res['sender'] = msg.sender
        res['sender_name'] = msg.sender_name
        res['receiver'] = msg.receiver
        res['receiver_name'] = msg.receiver_name
        res['subject'] = msg.subject
        res['message'] = msg.message
        res['created'] = str(msg.time_created)
        res['sent'] = msg.sent
        if msg.sent:
            res['time_sent'] = str(msg.time_sent)
        res['data'] = msg.data

        return res


import tornado.gen
@tornado.gen.coroutine
def send_mail_from_queue(sender, sender_name, receiver, receiver_name, subject, message, data, id_mail_queue):
    """
    Send mail over with Sendgrid SDK
    :param sender: str - email address of the sender
    :param sender_name: str - display name of the sender
    :param receiver:  str - email address of the receiver
    :param receiver_name: str - display name of the receiver
    :param subject: str - subject of the message
    :param message: str - body of the message
    :param data: dict - additional message data in json form
    :param id_mail_queue: int - id of the saved mail in mail_queue
    :return: dict - response from the Sendgrid SDK
    """

    import os
    import sendgrid

    if not os.environ.get('SENDGRID_API_KEY'):
        log.critical('The SENDGRID_API_KEY is not set, can not continue')
        return {'status': False}

    sg = sendgrid.SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))

    mail = {
        'personalizations': [
            {
                'to': [
                    {
                        'email': receiver,
                        'name': receiver_name
                    }
                ],
                'subject': subject
            }
        ],
        'from': {
            'email': sender,
            'name': sender_name
        },
        'content': [
            {
                'type': 'text/html',
                'value': message
            }
        ]
    }

    try:
        response = sg.send(mail)
    except Exception as e:
        log.critical('Error sending email over sendgrid: {}'.format(e))
        return {'status': False}

    if response.status_code < 300:
        log.info('Mail sent')
        res = {'status': True, 'time_sent': datetime.datetime.now()}
    else:
        log.info('Mail not sent')
        res = {'status': False}

    return res


def update_mail_status(id_mail_queue, sent_mail_response):

    import base.common.orm
    MailQueue = base.common.orm.get_orm_model('mail_queue')
    with base.common.orm.orm_session() as _session:

        _mail = _session.query(MailQueue).filter(MailQueue.id == id_mail_queue).one_or_none()
        if _mail is None:
            log.error('Can not find email with id {}'.format(id_mail_queue))
            return False

        log.info('UPDATE MAIL {} WITH {}'.format(id_mail_queue, sent_mail_response))
        _mail.sent = sent_mail_response['status'] if 'status' in sent_mail_response else True
        _mail.time_sent = sent_mail_response['time_sent'] if 'time_sent' in sent_mail_response else datetime.datetime.now()
        _session.commit()

    return True


def get_email_by_id(id_mail_queue):

    import base.common.orm
    MailQueue = base.common.orm.get_orm_model('mail_queue')
    with base.common.orm.orm_session() as _session:

        _mail = _session.query(MailQueue).filter(MailQueue.id == id_mail_queue).one_or_none()
        if _mail is None:
            log.error('Can not find email with id {}'.format(id_mail_queue))
            return False

        return {
            'id': id_mail_queue,
            'subject': _mail.subject,
            'sender_name': _mail.sender_name,
            'sender': _mail.sender,
            'receiver_name': _mail.receiver_name,
            'receiver': _mail.receiver,
            'time_created': _mail.time_created,
            'time_sent': _mail.time_sent,
            'sent': _mail.sent,
            'message': _mail.message,
            'data': _mail.data
        }

# END OF E-MAIL QUEUE

# FORGOT PASSWORD


def forgot_password(auth_user, data, sent=True):
    _data = {
        'cmd': 'forgot_password',
        'username': auth_user.username,
        'id_user': auth_user.id,
    }

    if data and isinstance(data, dict):
        _data.update(data)

    try:
        _hash = save_hash(_data)
    except SaveHash2ParamsException as e:
        log.critical('Error save hash for forgot password with data: {}; error: {}'.format(_data, e))
        return False

    _hash = _hash['h2p']

    from base.config.application_config import support_mail_address
    from base.config.application_config import support_name
    from base.config.application_config import forgot_password_message
    from base.config.application_config import forgot_password_message_subject
    from base.config.application_config import forgot_password_lending_address
    _receiver_name = auth_user.user.first_name \
        if hasattr(auth_user.user, 'first_name') and auth_user.user.first_name else auth_user.username
    _forgot_address = '{}/{}'.format(forgot_password_lending_address, _hash)
    _message = forgot_password_message.format(_forgot_address)

    res = save_mail_queue(
        support_mail_address,
        support_name,
        auth_user.username,
        _receiver_name,
        forgot_password_message_subject,
        _message,
        None,
        sent)
    
    return res


def find_user_and_forgot_password(username, data):

    import base.common.orm
    AuthUser = base.common.orm.get_orm_model('auth_users')
    with base.common.orm.orm_session() as _session:

        _user = _session.query(AuthUser).filter(AuthUser.username == username).one_or_none()

        if _user is None:
            log.warning('Non existing user {} request forgot password'.format(username))
            return False

        return forgot_password(_user, data, False)


# END OF FORGOT PASSWORD

def get_google_authorized_client_id(auth_data):

    import base.config.application_config
    return base.config.application_config.google_client_ID

