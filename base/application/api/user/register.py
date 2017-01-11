# coding= utf-8

import base.application.lookup.responses as msgs
from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.common.utils import get_request_ip
from base.common.utils import log


def user_exists(username, AuthUser, _session):
    _q = _session.query(AuthUser).filter(AuthUser.username == username)
    return _q.count() == 1


@api(
    URI='/user/register',
    PREFIX=False)
class Register(Base):

    @params(
        {'name': 'username', 'type': 'e-mail', 'required': True,  'doc': 'username to register'},
        {'name': 'password', 'type': str, 'required': True,  'doc': "user's password"},
        {'name': 'data', 'type': 'json', 'required': True,  'doc': "user's additional data"},
    )
    def post(self, username, password, data):
        """Register user on the system"""

        from base.application.api_hooks import api_hooks

        if hasattr(api_hooks, 'pre_register_user'):
            pre_reg_usr = api_hooks.pre_register_user(username, password, data)
            if pre_reg_usr is False:
                log.critical('Pre register user process error')
                return self.error(msgs.ERROR_USER_REGISTER)

        import base.common.orm
        AuthUsers, _session = base.common.orm.get_orm_model('auth_users')
        User, _ = base.common.orm.get_orm_model('users')

        if user_exists(username, AuthUsers, _session):
            log.warning('Username {} already taken, requested from {}'.format(username, get_request_ip(self)))
            return self.error(msgs.USERNAME_ALREADY_TAKEN)

        if base.config.application_config.strong_password and hasattr(api_hooks, 'check_password_is_valid'):
            if not api_hooks.check_password_is_valid(password):
                log.warning('Password {} is not valid'.format(password))
                return self.error(msgs.INVALID_PASSWORD)

        from base.common.sequencer import sequencer
        id_user = sequencer().new('u')

        if not id_user:
            return self.error(msgs.ERROR_USER_SEQUENCE)

        response = {}

        _user_registered = api_hooks.register_user(id_user, username, password, data)
        if _user_registered is None:
            log.critical('Error register user {} with password {} and data {}'.format(
                username, password, data))
            return self.error(msgs.ERROR_USER_REGISTER)

        if isinstance(_user_registered, dict):
            response.update(_user_registered)
        elif _user_registered != True:
            try:
                response['message'] = str(_user_registered)
            except Exception:
                log.error('Can not make string from user register response')

        from base.common.tokens_services import get_token
        _token = get_token(id_user, data)
        if not _token:
            log.critical('Error getting token for new user {} - {}'.format(id_user, username))
            return self.error(msgs.ERROR_RETRIEVE_SESSION)
        response.update(_token)

        if hasattr(api_hooks, 'post_register_process'):
            _post_register_result = api_hooks.post_register_process(id_user, username, password, data)
            if not _post_register_result:
                log.critical('Post register process error for user {} - {}'.format(id_user, username))
                return self.error(msgs.ERROR_USER_POSTREGISTER)

            if isinstance(_post_register_result, dict):
                response.update(_post_register_result)

        return self.ok(response)

