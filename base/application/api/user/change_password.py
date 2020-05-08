# coding= utf-8

import base.application.lookup.responses as msgs
from base.application.components import Base
from base.application.components import api
from base.application.components import authenticated
from base.application.components import params
from base.common.utils import format_password
from base.common.utils import log
from base.common.utils import password_match


@api(
    URI='/user/password/change/:hash',
    PREFIX=False,
    SPECIFICATION_PATH='User')
class ChangePassword(Base):

    @params(
        {'name': 'new_password', 'type': str, 'required': True,  'doc': "user's new password"},
        {'name': 'hash', 'type': str, 'required': True,  'doc': "hash from forgot password reset flow"},
    )
    def post(self, new_password, _hash):
        """Change user's password"""

        from base.application.api_hooks import api_hooks
        hash_data = api_hooks.get_hash_data(_hash)
        if 'id_user' not in hash_data:
            log.critical('Wrong hash data {} for change password request'.format(hash_data))
            return self.error(msgs.CHANGE_PASSWORD_ERROR)

        _id = hash_data['id_user']

        import base.common.orm
        AuthUser = base.common.orm.get_orm_model('auth_users')
        with base.common.orm.orm_session() as _session:
            _q = _session.query(AuthUser).filter(AuthUser.id == _id)
            if _q.count() == 0:
                log.critical('User {} not found for change password'.format(_id))
                _session.close()
                return self.error(msgs.USER_NOT_FOUND)

            user = _q.one()

            _password = format_password(user.username, new_password)
            user.password = _password
            _session.commit()

        return self.ok()


@authenticated()
@api(
    URI='/user/password/change',
    PREFIX=False,
    SPECIFICATION_PATH='User')
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
            return self.error(msgs.UNAUTHORIZED_REQUEST, http_status=403)

        _password = format_password(self.auth_user.username, new_password)
        self.auth_user.password = _password
        self.orm_session.commit()

        return self.ok()
