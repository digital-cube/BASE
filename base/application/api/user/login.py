# coding= utf-8

import json

import base.application.lookup.responses as msgs
from base.application.components import Base
from base.application.components import api
from base.application.components import authenticated
from base.application.components import params
from base.application.helpers.exceptions import CheckUserError
from base.application.helpers.exceptions import PreCheckUserError
from base.application.helpers.exceptions import PostCheckUserError
from base.application.helpers.exceptions import PostLoginException
from base.application.helpers.exceptions import PreLoginException
from base.common.tokens_services import get_token
from base.common.utils import log


@api(
URI='/user/login',
    PREFIX=False,
    SPECIFICATION_PATH='User')
class Login(Base):

    @authenticated()
    def get(self):
        """Login user - check user is logged in"""

        from base.application.api_hooks import api_hooks

        _pre_check = None
        if hasattr(api_hooks, 'pre_check_user'):
            try:
                _pre_check = api_hooks.pre_check_user(self.auth_user)
            except PreCheckUserError as e:
                log.critical('Pre check user {} error: {}'.format(self.auth_user.id, e))
                return self.error(msgs.PRE_CHECK_USER_ERROR)

        try:
            _check_user = api_hooks.check_user(self.auth_user, request_handler=self)
        except CheckUserError as e:
            log.critical('Check user {} error {}'.format(self.auth_user.id, e))
            return self.error(msgs.CHECK_USER_ERROR)

        if _pre_check is not None and isinstance(_pre_check, dict):
            _check_user.update(_pre_check)

        if hasattr(api_hooks, 'post_check_user'):
            try:
                _post_check = api_hooks.post_check_user(self.auth_user)
            except PostCheckUserError as e:
                log.critical('Post check user {} error: {}'.format(self.auth_user.id, e))
                return self.error(msgs.POST_CHECK_USER_ERROR)
            if isinstance(_post_check, dict):
                _check_user.update(_post_check)

        return self.ok(_check_user)

    @params(
        {'name': 'username', 'type': 'e-mail', 'required': True,  'doc': "user's username"},
        {'name': 'password', 'type': str, 'required': True,  'doc': "user's password"},
        {'name': 'data', 'type': 'json', 'required': False,  'doc': "user's additional data"},
    )
    def post(self, username, password, data):
        """Login user - retrieve session"""

        from base.application.api_hooks import api_hooks
        user = api_hooks.user_exists(username, password, data, self)
        if not user:
            return self.error(msgs.WRONG_USERNAME_OR_PASSWORD)

        if not api_hooks.check_username_and_password(username, password, user):
            return self.error(msgs.WRONG_USERNAME_OR_PASSWORD)

        _pre_login = None
        if hasattr(api_hooks, 'pre_login_process'):
            try:
                _pre_login = api_hooks.pre_login_process(user, data, request_handler=self)
            except PreLoginException as e:
                log.critical('Pre login error: {}'.format(e))
                return self.error(msgs.PRE_LOGIN_ERROR)

        _token = get_token(user.id, data)
        if not _token:
            log.critical('Error getting token for user {} - {}'.format(user.id, username))
            return self.error(msgs.ERROR_RETRIEVE_SESSION)

        _post_login = None
        if hasattr(api_hooks, 'post_login_process'):
            try:
                _post_login = api_hooks.post_login_process(user, data, _token, request_handler=self)
            except PostLoginException as e:
                log.critical('Post login error: {}'.format(e))
                return self.error(msgs.POST_LOGIN_ERROR)

        response = {}
        response.update(_token)
        self.set_authorized_cookie(_token)

        self.update_res(_pre_login, response)
        self.update_res(_post_login, response)

        return self.ok(response)

    def update_res(self, _data, _res):

        if _data and isinstance(_data, dict):
            _res.update(_data)

        if _data and isinstance(_data, str):
            _res.update({'data': _data})

