# coding= utf-8

import json
import base.application.lookup.responses as msgs
from base.common.utils import log
from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.common.tokens_services import get_token
from base.application.helpers.exceptions import CheckUserError
from base.application.helpers.exceptions import PreLoginException
from base.application.helpers.exceptions import PostLoginException
from base.application.components import authenticated


@api(
    URI='/user/forgot',
    PREFIX=False)
class Forgot(Base):

    @params(
        {'name': 'username', 'type': 'e-mail', 'required': True,  'doc': "user's username"},
        {'name': 'data', 'type': json, 'required': False,  'doc': "request additional data"},
    )
    def put(self, username, data):
        """Start user forgot password process"""

        import base.common.orm
        AuthUser, _session = base.common.orm.get_orm_model('auth_users')

        _q = _session.query(AuthUser).filter(AuthUser.username == username)

        if _q.count() == 0:
            log.warning('Non existing user {} request forgot password'.format(username))
            return self.error(msgs.USER_NOT_FOUND)

        user = _q.one()

        from base.application.api import api_hooks
        if not api_hooks.forgot_password(user, data):
            return self.error(msgs.FORGOT_REQUEST_ERROR)

        return self.ok()
    #     from base.application.api import api_hooks
    #     user = api_hooks.user_exists(username)
    #     if not user:
    #         return self.error(msgs.WRONG_USERNAME_OR_PASSWORD)
    #
    #     if not api_hooks.check_username_and_password(username, password, user):
    #         return self.error(msgs.WRONG_USERNAME_OR_PASSWORD)
    #
    #     _pre_login = None
    #     if hasattr(api_hooks, 'pre_login_process'):
    #         try:
    #             _pre_login = api_hooks.pre_login_process(user, data)
    #         except PreLoginException as e:
    #             log.critical('Pre login error: {}'.format(e))
    #             return self.error(msgs.PRE_LOGIN_ERROR)
    #
    #     _token = get_token(user.id)
    #     if not _token:
    #         log.critical('Error getting token for user {} - {}'.format(user.id, username))
    #         return self.error(msgs.ERROR_RETRIEVE_SESSION)
    #
    #     _post_login = None
    #     if hasattr(api_hooks, 'post_login_process'):
    #         try:
    #             _post_login = api_hooks.post_login_process(user, data)
    #         except PostLoginException as e:
    #             log.critical('Post login error: {}'.format(e))
    #             return self.error(msgs.POST_LOGIN_ERROR)
    #
    #     response = {}
    #     response.update(_token)
    #
    #     self.update_res(_pre_login, response)
    #     self.update_res(_post_login, response)
    #
    #     return self.ok(response)
    #
    # def update_res(self, _data, _res):
    #
    #     if _data and isinstance(_data, dict):
    #         _res.update(_data)
    #
    #     if _data and isinstance(_data, str):
    #         _res.update({'data': _data})

