# coding= utf-8

from base.application.components import Base
from base.application.components import api


@api(
    URI='/option',
    PREFIX=False)
class Options(Base):

    def get(self):
        return self.ok('options get')

