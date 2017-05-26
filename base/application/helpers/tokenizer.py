# coding= utf-8

import base.application.lookup.session_token_type as session_token_type


class Tokenizer(object):
    """Tokenizer prototype class"""

    def __init__(self):
        from base.common.utils import log
        self.log = log

    def get_assigned_token(self, uid, data, token_type=session_token_type.SIMPLE):
        """
        get token from database
        :param uid: user id
        :param data: additional data in dictionary
        :param token_type:  type of the token
        :return:  token and it's type or error
        """
        raise NotImplemented('get_assigned_token has to be implemented')

    def set_session_token(self, uid, data, token_type=session_token_type.SIMPLE):
        """
        set token in database
        :param uid: user id
        :param data: additional data in dictionary
        :param token_type:  type of the token
        :return: new token and it's type
        """
        raise NotImplemented('set_session_token has to be implemented')

    def get_user_by_token(self, tk, pack=True):
        """
        retrieve user by given token
        :param tk: session token
        :param pack: whether to return packed or orm user
        :return: packed user if pack else AuthUser
        """
        raise NotImplemented('get_user_by_token has to be implemented')

    def close_session(self, tk):
        """
        close session by given token
        :param tk: session token
        :return:  True/False
        """
        raise NotImplemented('close_session has to be implemented')

