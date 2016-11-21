# coding= utf-8

import base.application.lookup.responses as msgs
from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.common.utils import log
from base.common.utils import get_request_ip


def user_exists(username, AuthUser):
    import base.common.orm
    _session = base.common.orm.orm.session()
    _q = _session.query(AuthUser).filter(AuthUser.username == username)
    return _q.count() == 1


@api(
    URI='/register',
    PREFIX=False)
class Register(Base):

    @params(
        {'name': 'username', 'type': 'e-mail', 'required': True,  'doc': 'username to register'},
        {'name': 'password', 'type': str, 'required': True,  'doc': "user's password"},
        {'name': 'data', 'type': 'json', 'required': True,  'doc': "user's additional data"},
    )
    def post(self, username, password, data):

        import base.config.application_config
        print('MODES2', base.config.application_config.orm_models)
        AuthUsers = base.config.application_config.orm_models['auth_users']
        User = base.config.application_config.orm_models['users']

        if user_exists(username, AuthUsers):
            log.warning('Username {} already taken, requested from {}'.format(username, get_request_ip(self)))
            return self.error(msgs.USERNAME_ALREADY_TAKEN)

        from base.application.api import api_hooks
        if base.config.application_config.strong_password and hasattr(api_hooks, 'check_password_is_valid'):
            if not api_hooks.check_password_is_valid(password):
                log.warning('Password {} is not valid'.format(password))
                return self.error(msgs.INVALID_PASSWORD)

        # TODO: problem with sequencer orm connection - cannot get session
        # from base.common.sequencer import sequencer
        # id_user = sequencer().new('u')
        # TODO: remove this id making
        import datetime, hashlib
        id_user = hashlib.md5(str(datetime.datetime.now()).encode('utf-8')).hexdigest()[:10]

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
        elif _user_registered is not None:
            try:
                response['message'] = str(_user_registered)
            except Exception:
                log.error('Can not make string from user register response')

        if hasattr(api_hooks, 'post_register_process'):
            api_hooks.post_register_process(usernam)

        return self.ok(response)
