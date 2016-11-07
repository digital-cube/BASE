# coding= utf-8

from base.application.components import Base
from base.application.components import api
from base.application.components import params


@api(
    URI='/option/:key',
    PREFIX=False)
class Options(Base):

    @params(
        {'name': 'id', 'type': 'str', 'min': 10, 'max': 20, 'doc': 'id of a option', 'default': 'id_bla'},
        {'name': 'value', 'type': int, 'required': True,  'min': 20, 'max': 30, 'doc': 'value of a option'},
        {'name': 'key', 'type': 'str', 'required': True,  'min': 20, 'max': 30, 'doc': 'key of a option'},
    )
    def get(self, id, value, key):
        print('Here it is', id, type(id))
        print('Here is another one', value, type(value))
        print('Here is a key', key, type(key))
        return self.ok('options get')

