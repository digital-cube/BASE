# coding= utf-8

import base.application.lookup.responses as msgs
from base.common.utils import log
from base.application.components import Base
from base.application.components import api
from base.application.components import authenticated
from base.common.tokens_services import close_session

@authenticated()
@api(
    URI='/logout',
    PREFIX=False)
class Logout(Base):

    def post(self, *args):
        """Logout user - close session"""

        if not close_session(self.auth_token):
            log.critical('Can not logout user with token {}'.format(self.auth_token))
            return self.error(msgs.LOGOUT_ERROR)

        return self.ok()

