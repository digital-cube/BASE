# coding= utf-8

from base.application.components import Base
from base.application.components import api


@api(
    URI='/',
    PREFIX=False)
class Login(Base):

    def get(self):
        return self.ok('login')
