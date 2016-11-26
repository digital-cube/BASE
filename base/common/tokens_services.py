# coding= utf-8

from sqlalchemy import desc
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

    def get_assigned_token(self, uid, token_type=session_token_type.SIMPLE):
        """get token from database"""
        raise NotImplemented('get_assigned_token has to be implemented')

    def set_session_token(self, uid, tk, token_type=session_token_type.SIMPLE):
        """set token in database"""
        raise NotImplemented('set_session_token has to be implemented')


class SqlTokenizer(Tokenizer):
    """Session tokens from sql database"""

    def __init__(self):
        super(SqlTokenizer, self).__init__()

    def get_assigned_token(self, uid, token_type=session_token_type.SIMPLE):
        """get token from database"""

        import base.config.application_config
        import base.common.orm
        SessionToken = base.config.application_config.orm_models['session_tokens']
        _session = base.common.orm.orm.session()
        _q = _session.query(SessionToken).filter(
            SessionToken.id_user == uid, SessionToken.active, SessionToken.type == token_type).order_by(
            desc(SessionToken.created))

        _session_token = _q.first()
        if _session_token is None:
            log.info('No active session for user {} found'.format(uid))
            return _session_token

        return {"token_type": session_token_type.lmap[_session_token.type], "token": _session_token.id}

    def set_session_token(self, uid, tk, token_type=session_token_type.SIMPLE):
        """set token in database"""
        print('SET', )

        import base.config.application_config
        import base.common.orm
        SessionToken = base.config.application_config.orm_models['session_tokens']
        _session = base.common.orm.orm.session()

        _id_session_token = sequencer().new('s')
        if not _id_session_token:
            log.critical('Can not set users {} session token'.format(uid))
            raise ErrorSetSessionToken('Error setting token')

        _session_token = SessionToken(_id_session_token, uid, type=token_type)
        _session.add(_session_token)
        _session.commit()

        return {'token_type': session_token_type.lmap[_session_token.type], 'token': _id_session_token}


class RedisTokenizer(Tokenizer):
    """Session tokens from redis database"""

    def __init__(self):
        super(RedisTokenizer, self).__init__()

    def get_assigned_token(self, uid, token_type=session_token_type.SIMPLE):
        """get token from database"""
        return {"token_type": session_token_type.lmap[session_token_type.SIMPLE], "token": "asdfasdfaf"}

    def set_session_token(self, uid, tk, token_type=session_token_type.SIMPLE):
        """set token in database"""
        print('SET', )


def get_token(uid, token_type=session_token_type.SIMPLE):
    # RETRIEVE ASSIGNED TOKEN
    _tokenizer = Tokenizer.get_tokenizer()
    __tk = _tokenizer.get_assigned_token(uid, token_type)
    if __tk:
        return __tk

    # MAKE NEW TOKEN
    __tk = sequencer().new('s')

    try:
        return _tokenizer.set_session_token(uid, __tk, token_type)
    except ErrorSetSessionToken:
        return None
