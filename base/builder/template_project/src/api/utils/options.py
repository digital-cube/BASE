# coding= utf-8

from base.application.components import base
from base.application.components import api


@api(
    URI='/option',
    PREFIX=False)
class Options(base):

    def get(self):
        return self.ok('drz bre ovaj')

