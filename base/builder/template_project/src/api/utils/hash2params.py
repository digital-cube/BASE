# coding= utf-8

from base.application.components import Base
from base.application.components import api


@api(
    URI='/h2p',
    PREFIX=False)
class Hash2Params(Base):

    def get(self):
        return self.ok('get h2p')
