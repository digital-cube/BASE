# coding= utf-8

import base.application.lookup.responses as msgs
from base.common.utils import log
from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.common.tokens_services import get_token
from base.application.api.api_hooks import user_exists
from base.application.api.api_hooks import check_username_and_password


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

        user = user_exists(username)
        if not user:
            return self.error(msgs.WRONG_USERNAME_OR_PASSWORD)

        if not check_username_and_password(username, password, user):
            return self.error(msgs.WRONG_USERNAME_OR_PASSWORD)

        _token = get_token(user.id)
        if not _token:
            log.critial('Error getting token for user {} - {}'.format(user.id, username))
            return self.error(msgs.ERROR_RETRIEVE_SESSION)

        response = {}
        response.update(_token)

        return self.ok(response)

