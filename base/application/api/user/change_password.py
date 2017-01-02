# coding= utf-8

import json
import base.application.lookup.responses as msgs
from base.common.utils import log
from base.common.utils import format_password
from base.common.utils import password_match
from base.common.tokens_services import get_user_by_token
from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.common.tokens_services import get_token
from base.application.helpers.exceptions import CheckUserError
from base.application.helpers.exceptions import PreLoginException
from base.application.helpers.exceptions import PostLoginException
from base.application.components import authenticated


@api(
    URI='/user/password/change/:hash',
    PREFIX=False)
class ChangePassword(Base):

    @params(
        {'name': 'new_password', 'type': str, 'required': True,  'doc': "user's new password"},
        {'name': 'hash', 'type': str, 'required': True,  'doc': "hash from forgot password reset flow"},
    )
    def post(self, new_password, _hash):
        """Change user's password"""

        from base.application.api import api_hooks
        hash_data = api_hooks.get_hash_data(_hash)
        if 'id_user' not in hash_data:
            log.critical('Wrong hash data {} for change password request'.format(hash_data))
            return self.error(msgs.CHANGE_PASSWORD_ERROR)

        _id = hash_data['id_user']

        import base.common.orm
        AuthUser, _session = base.common.orm.get_orm_model('auth_users')
        _q = _session.query(AuthUser).filter(AuthUser.id == _id)
        if _q.count() == 0:
            log.critical('User {} not found for change password'.format(_id))
            return self.error(msgs.USER_NOT_FOUND)

        user = _q.one()

        _password = format_password(user.username, new_password)
        user.password = _password
        _session.commit()

        return self.ok()


@authenticated()
@api(
    URI='/user/password/change',
    PREFIX=False)
class UserChangePassword(Base):

    @params(
        {'name': 'old_password', 'type': str, 'required': True,  'doc': "user's old password"},
        {'name': 'new_password', 'type': str, 'required': True,  'doc': "user's new password"}
    )
    def post(self, old_password, new_password):
        """User change password"""

        if not password_match(self.auth_user.username, old_password, self.auth_user.password):
            log.critical('User {} trying to change password to {} with wrong password {}'.format(
                self.auth_user.id, new_password, old_password))
            return self.error(msgs.UNAUTHORIZED_REQUEST)

        import base.common.orm
        AuthUser, _session = base.common.orm.get_orm_model('auth_users')

        _password = format_password(self.auth_user.username, new_password)
        self.auth_user.password = _password
        _session.commit()

        return self.ok()
