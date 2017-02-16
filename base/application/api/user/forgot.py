# coding= utf-8

import json

import base.application.lookup.responses as msgs
from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.common.utils import log


@api(
    URI='/user/forgot',
    PREFIX=False,
    SPECIFICATION_PATH='User')
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

        from base.application.api_hooks import api_hooks
        if not api_hooks.forgot_password(user, data):
            return self.error(msgs.FORGOT_REQUEST_ERROR)

        return self.ok()

