# coding= utf-8

from base.application.components import Base
from base.application.components import api
from base.common.tokens_services import get_token


@api(
    URI='/login',
    PREFIX=False)
class Login(Base):

    def post(self):

        _uid = 'asdf'
        _token = get_token(_uid)

        return self.ok(_token)
