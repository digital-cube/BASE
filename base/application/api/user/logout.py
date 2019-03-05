# coding= utf-8

import base.application.lookup.responses as msgs
from base.application.components import Base
from base.application.components import api
from base.application.components import authenticated
from base.application.helpers.exceptions import PostLogoutException
from base.application.helpers.exceptions import PreLogoutException
from base.common.tokens_services import close_session
from base.common.utils import log


@authenticated()
@api(
    URI='/user/logout',
    PREFIX=False,
    SPECIFICATION_PATH='User')
class Logout(Base):

    def post(self, *args):
        """Logout user - close session"""

        from base.application.api_hooks import api_hooks
        _res = {}
        _pre_logout = None
        if hasattr(api_hooks, 'pre_logout_process'):
            try:
                _pre_logout = api_hooks.pre_logout_process(self.auth_user)
            except PreLogoutException as e:
                log.critical('Pre logout error: {}'.format(e))
                return self.error(msgs.PRE_LOGOUT_ERROR)

        if isinstance(_pre_logout, dict):
            _res.update(_pre_logout)

        if not close_session(self.auth_token):
            log.critical('Can not logout user with token {}'.format(self.auth_token))
            return self.error(msgs.LOGOUT_ERROR)

        _post_logout = None
        if hasattr(api_hooks, 'post_logout_process'):
            try:
                _post_logout = api_hooks.post_logout_process(self.auth_user, self.auth_token)
            except PostLogoutException as e:
                log.critical('Post logout error: {}'.format(e))
                return self.error(msgs.POST_LOGOUT_ERROR)

        if isinstance(_post_logout, dict):
            _res.update(_post_logout)

        self.remove_authorized_cookie()
        if _res:
            return self.ok(_res)

        return self.ok()

