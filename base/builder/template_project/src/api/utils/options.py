# coding= utf-8

from base.application.components import Base
from base.application.components import api
from base.application.components import params


@api(
    URI='/option',
    PREFIX=False)
class Options(Base):

    @params(
        {'name': 'id', 'type': 'str', 'min': 10, 'max': 20, 'doc': 'id of a option', 'default': 'id_bla'},
        {'name': 'value', 'type': int, 'required': True,  'min': 20, 'max': 30, 'doc': 'value of a option'},
    )
    def get(self, id, name):
        print('Here it is', id, type(id))
        print('Here is another one', name, type(name))
        return self.ok('options get')

