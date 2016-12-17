# coding= utf-8

import base.application.lookup.responses as msgs
from base.common.utils import log
from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.common.tokens_services import get_token
from base.application.helpers.exceptions import PreLoginException
from base.application.helpers.exceptions import PostLoginException


@api(
    URI='/login',
    PREFIX=False)
class Login(Base):

    @params(
        {'name': 'username', 'type': 'e-mail', 'required': True,  'doc': "user's username"},
        {'name': 'password', 'type': str, 'required': True,  'doc': "user's password"},
    )
    def post(self, username, password):
        """Login user - retrieve session"""

        from base.application.api import api_hooks
        user = api_hooks.user_exists(username)
        if not user:
            return self.error(msgs.WRONG_USERNAME_OR_PASSWORD)

        if not api_hooks.check_username_and_password(username, password, user):
            return self.error(msgs.WRONG_USERNAME_OR_PASSWORD)

        _pre_login = None
        if hasattr(api_hooks, 'pre_login_process'):
            try:
                _pre_login = api_hooks.pre_login_process(user)
            except PreLoginException as e:
                log.critial('Pre login error: {}'.format(e))
                return self.error(msgs.PRE_LOGIN_ERROR)

        _token = get_token(user.id)
        if not _token:
            log.critial('Error getting token for user {} - {}'.format(user.id, username))
            return self.error(msgs.ERROR_RETRIEVE_SESSION)

        _post_login = None
        if hasattr(api_hooks, 'post_login_process'):
            try:
                _post_login = api_hooks.post_login_process(user)
            except PostLoginException as e:
                log.critial('Post login error: {}'.format(e))
                return self.error(msgs.POST_LOGIN_ERROR)

        response = {}
        response.update(_token)

        self.update_res(_pre_login, response)
        self.update_res(_post_login, response)

        return self.ok(response)

    def update_res(self, _data, _res):

        if _data and isinstance(_data, dict):
            _res.update(_data)

        if _data and isinstance(_data, str):
            _res.update({'data': _data})

