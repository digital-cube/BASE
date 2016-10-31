# coding= utf-8

from base.application.components import base
from base.application.components import api


@api(
    URI='/h2p',
    PREFIX=False)
class Hash2Params(base):

    def get(self):
        return self.ok('evo ti has bre')

