# coding= utf-8

import datetime
from sqlalchemy import desc

import base.application.lookup.session_token_type as session_token_type
from base.application.helpers.exceptions import ErrorSetSessionToken
from base.common.sequencer import sequencer

from base.application.helpers.tokenizer import Tokenizer


class SqlTokenizer(Tokenizer):
    """
    Session tokens from sql database
    """

    def __init__(self):
        super(SqlTokenizer, self).__init__()

    def get_assigned_token(self, uid, data, token_type=session_token_type.SIMPLE):
        """
        get token from database
        :param uid: user id
        :param data: additional data in dictionary
        :param token_type:  type of the token
        :return:  token and it's type or error
        """

        import base.common.orm
        SessionToken = base.common.orm.get_orm_model('session_tokens')
        with base.common.orm.orm_session() as _session:
            
            _q = _session.query(SessionToken).filter(
                SessionToken.id_user == uid, SessionToken.active, SessionToken.type == token_type).order_by(
                desc(SessionToken.created))

            _session_token = _q.first()
            if _session_token is None:
                return _session_token
            
            import base.config.application_config as cfg

            if hasattr(cfg, 'session_expiration_timeout') and cfg.session_expiration_timeout is not None:
                _session_life_time_in_seconds = (datetime.datetime.now() - _session_token.last_used).seconds
                if _session_life_time_in_seconds > cfg.session_expiration_timeout:
                    self.log.warning('Session {} expired, last used {}, closing session'.format(_session_token.id, _session_token.last_used))
                    _session_token.active = False
                    _session.commit()
                    return None

        return {"token_type": session_token_type.lmap[_session_token.type], "token": _session_token.id}

    def set_session_token(self, uid, data, token_type=session_token_type.SIMPLE):
        """
        set token in database
        :param uid: user id
        :param data: additional data in dictionary
        :param token_type:  type of the token
        :return: new token and it's type
        """

        import base.common.orm
        SessionToken = base.common.orm.get_orm_model('session_tokens')
        with base.common.orm.orm_session() as _session:
            # MAKE NEW TOKEN
            _tk = sequencer().new('s', session=_session)

            if not _tk:
                self.log.critical('Can not set users {} session token'.format(uid))
                raise ErrorSetSessionToken('Error setting token')

            _session_token = SessionToken(_tk, uid, type=token_type)
            _session.add(_session_token)
            _session.commit()

            return {'token_type': session_token_type.lmap[_session_token.type], 'token': _tk}

    def get_user_by_token(self, tk, pack=True, orm_session=None, request_handler=None):
        """
        retrieve user by given token
        :param tk: session token
        :param pack: whether to return packed or orm user
        :param orm_session: SQLAlchemy session
        :param request_handler: the request handler which called the method
        :return: packed user if pack else AuthUser
        """

        import base.common.orm
        SessionToken = base.common.orm.get_orm_model('session_tokens')
        AuthUser = base.common.orm.get_orm_model('auth_users')

        import base.application.api_hooks.api_hooks
        import base.config.application_config as cfg
        with base.common.orm.orm_session() as _session:
            if orm_session:
                _session = orm_session

            _qs = _session.query(SessionToken).filter(SessionToken.id == tk)

            if _qs.count() != 1:
                self.log.critical('Cannot retrieve session with id: {}'.format(tk))
                return None

            _db_session = _qs.one()

            if not _db_session.active:
                self.log.critical('Session {} is not active'.format(tk))
                return None
            
            if hasattr(cfg, 'session_expiration_timeout') and cfg.session_expiration_timeout is not None:
                _session_life_time_in_seconds = (datetime.datetime.now() - _db_session.last_used).seconds
                if _session_life_time_in_seconds > cfg.session_expiration_timeout:
                    self.log.warning('Session {} expired, last used {}, closing session'.format(tk, _db_session.last_used))
                    _db_session.active = False
                    _session.commit()
                    return None

            _q = _session.query(AuthUser).filter(AuthUser.id == _db_session.id_user)
            if _q.count() != 1:
                self.log.critical('User {} not found'.format(_db_session.id_user))
                return None

            _user = _q.one()

            if not _user.active:
                self.log.critical('User {} -> {} is not active'.format(_user.id, _user.username))
                return None
            
            _db_session.last_used = datetime.datetime.now()
            _session.commit()

            _packed_user = base.application.api_hooks.api_hooks.pack_user(_user) if pack else _user

        return _packed_user

    def close_session(self, tk):
        """
        close session by given token
        :param tk: session token
        :return:  True/False
        """

        import base.common.orm
        SessionToken = base.common.orm.get_orm_model('session_tokens')
        with base.common.orm.orm_session() as _session:

            _q = _session.query(SessionToken).filter(SessionToken.id == tk)

            if _q.count() != 1:
                self.log.critical('Session {} not found'.format(tk))
                return False

            _db_session = _q.one()
            _db_session.active = False
            self.log.info('Closing {} session'.format(tk))
            _session.commit()

        return True


class RedisTokenizer(Tokenizer):
    """Session tokens from redis database"""

    def __init__(self):
        super(RedisTokenizer, self).__init__()

    def get_assigned_token(self, uid, data, token_type=session_token_type.SIMPLE):
        """
        get token from database
        :param uid: user id
        :param data: additional data in dictionary
        :param token_type:  type of the token
        :return:  token and it's type or error
        """
        return {"token_type": session_token_type.lmap[session_token_type.SIMPLE], "token": "asdfasdfaf"}

    def set_session_token(self, uid, data, token_type=session_token_type.SIMPLE):
        """
        set token in database
        :param uid: user id
        :param data: additional data in dictionary
        :param token_type:  type of the token
        :return: new token and it's type
        """
        print('SET', )

    def get_user_by_token(self, tk, pack=True, orm_session=None, request_handler=None):
        """
        retrieve user by given token
        :param tk: session token
        :param pack: whether to return packed or orm user
        :param orm_session: orm session to be used
        :param request_handler: the request handler which initialized the request
        :return: packed user if pack else AuthUser
        """
        print('GET USER')

    def close_session(self, tk):
        """
        close session by given token
        :param tk: session token
        :return:  True/False
        """
        print('CLOSE SESSION')
