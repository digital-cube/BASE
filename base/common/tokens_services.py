# coding= utf-8

import base.application.lookup.session_storage as session_storage
import base.application.lookup.session_token_type as session_token_type
import base.config.application_config as application_config
from base.application.helpers.exceptions import ErrorSetSessionToken
from base.application.helpers.exceptions import UnknownSessionStorage
from base.common.utils import log


def get_tokenizer():

    import base.application.api_hooks.api_hooks as api_hooks
    if application_config.session_storage not in session_storage.lrev:
        log.critical('Unknown session storage configured: {}'.format(application_config.session_storage))
        raise UnknownSessionStorage('Session storage {} unknown'.format(application_config.session_storage))

    if session_storage.lrev[application_config.session_storage] == session_storage.REDIS:
        return api_hooks.RedisTokenizer()

    return api_hooks.SqlTokenizer()


def get_token(uid, data, token_type=session_token_type.SIMPLE):
    # RETRIEVE ASSIGNED TOKEN
    _tokenizer = get_tokenizer()
    __tk = _tokenizer.get_assigned_token(uid, data, token_type)
    if __tk:
        return __tk

    try:
        return _tokenizer.set_session_token(uid, data, token_type)
    except ErrorSetSessionToken:
        return None


def get_user_by_token(_token, pack=True, orm_session=None, request_handler=None):

    _tokenizer = get_tokenizer()
    return _tokenizer.get_user_by_token(_token, pack, orm_session, request_handler)


def close_session(_token):

    _tokenizer = get_tokenizer()
    return _tokenizer.close_session(_token)

