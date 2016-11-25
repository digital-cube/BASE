import base.application.lookup.session_token_type as session_token_type
import base.application.lookup.session_storage as session_storage
import base.config.application_config as application_config
from base.application.helpers.exceptions import UnknownSessionStorage
from base.application.helpers.exceptions import ErrorSetSessionToken
from base.common.utils import log
from base.common.sequencer import sequencer


class Tokenizer(object):

    @staticmethod
    def get_tokenizer():

        if application_config.session_storage not in session_storage.lrev:
            log.critical('Unknown session storage configured: {}'.format(application_config.session_storage))
            raise UnknownSessionStorage('Session storage {} unknown'.format(application_config.session_storage))

        if session_storage.lrev[application_config.session_storage] == session_storage.REDIS:
            return RedisTokenizer()

        return SqlTokenizer()

    def __init__(self):
        pass

    def get_assigned_token(self, uid):
        """get token from database"""
        raise NotImplemented('get_assigned_token has to be implemented')

    def set_session_token(self, uid, tk):
        """set token in database"""
        raise NotImplemented('set_session_token has to be implemented')


class SqlTokenizer(Tokenizer):
    """Session tokens from sql database"""

    def __init__(self):
        super(SqlTokenizer, self).__init__()

    def get_assigned_token(self, uid):
        """get token from database"""

        return {"token_type": session_token_type.lmap[session_token_type.SIMPLE], "token": "asdfasdfaf"}

    def set_session_token(self, uid, tk):
        """set token in database"""
        print('SET', )


class RedisTokenizer(Tokenizer):
    """Session tokens from redis database"""

    def __init__(self):
        super(RedisTokenizer, self).__init__()

    def get_assigned_token(self, uid):
        """get token from database"""
        return {"token_type": session_token_type.lmap[session_token_type.SIMPLE], "token": "asdfasdfaf"}

    def set_session_token(self, uid, tk):
        """set token in database"""
        print('SET', )


def get_token(uid):

    # RETRIEVE ASSIGNED TOKEN
    _tokenizer = Tokenizer.get_tokenizer()
    __tk = _tokenizer.get_assigned_token(uid)
    if __tk:
        return __tk

    __tk = sequencer().new('s')

    try:
        _tokenizer.set_session_token(uid, __tk)
    except ErrorSetSessionToken:
        return None

    return __tk


