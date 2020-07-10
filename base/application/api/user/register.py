# coding= utf-8

import base.application.lookup.responses as msgs
from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.application.components import RequestAuthenticationChecker
from base.common.utils import get_request_ip
from base.common.utils import log
from base.common.utils import user_exists


@api(
    URI='/user/register',
    PREFIX=False,
    SPECIFICATION_PATH='User')
class Register(Base):

    @params(
        {'name': 'username', 'type': 'e-mail', 'required': True,  'doc': 'username to register', 'lowercase': True},
        {'name': 'password', 'type': str, 'required': True,  'doc': "user's password"},
        {'name': 'data', 'type': 'json', 'required': False,  'doc': "user's additional data"},
    )
    def post(self, username, password, data):
        """Register user on the system"""

        from base.application.api_hooks import api_hooks

        import base.config
        if base.config.application_config.register_allowed_roles is not None:
            test_roles, roles_error = self.check_role_flags(data, base.config.application_config.register_allowed_roles)
            if not test_roles:
                return self.error(roles_error)

        username = username.strip()
        if hasattr(api_hooks, 'pre_register_user'):
            pre_reg_usr = api_hooks.pre_register_user(username, password, data, request_handler=self)
            if pre_reg_usr is False:
                log.critical('Pre register user process error')
                return self.error(msgs.ERROR_USER_REGISTER)

        import base.common.orm
        with base.common.orm.orm_session() as _session:
            
            AuthUsers = base.common.orm.get_orm_model('auth_users')

            if user_exists(username, AuthUsers, _session):
                log.warning('Username {} already taken, requested from {}'.format(username, get_request_ip(self)))
                return self.error(msgs.USERNAME_ALREADY_TAKEN)

        if base.config.application_config.strong_password and hasattr(api_hooks, 'check_password_is_valid'):
            if not api_hooks.check_password_is_valid(password):
                log.warning('Password {} is not valid'.format(password))
                return self.error(msgs.INVALID_PASSWORD)

        from base.common.sequencer import sequencer
        with base.common.orm.orm_session() as _s_session:
            id_user = sequencer().new('u', session=_s_session)
            _s_session.commit()

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
            _post_register_result = api_hooks.post_register_process(id_user, username, password, data, _token,
                                                                    request_handler=self)
            if not _post_register_result:
                log.critical('Post register process error for user {} - {}'.format(id_user, username))
                return self.error(msgs.ERROR_USER_POSTREGISTER)

            if isinstance(_post_register_result, dict):
                response.update(_post_register_result)

        self.set_authorized_cookie(_token)

        return self.ok(response)

    def check_role_flags(self, data, allowed_roles):

        # check if role is sent
        if 'role_flags' not in data:
            log.error('Missing role flags in data: {}'.format(data))
            return False, msgs.ERROR_USER_REGISTER

        # check if role flag is valid value
        if not isinstance(data['role_flags'], int):
            log.error('Wrong role flags type: {}'.format(data))
            return False, msgs.WRONG_ROLE_TYPE

        # check if role is allowed
        if not (data['role_flags'] & allowed_roles):

            import base.config.application_config
            auth_checker = RequestAuthenticationChecker(self, base.config.application_config.registrators_allowed_roles)

            if not auth_checker.is_authenticated():
                log.error('Registration is not authenticated')
            if self.auth_token is None or self.auth_user is None:
                log.error('Unauthorized user trying to register an account with data: {}'.format(data))
                return False, msgs.UNAUTHORIZED_REQUEST

        return True, ''

