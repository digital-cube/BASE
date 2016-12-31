# coding= utf-8

from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.application.components import authenticated


# @authenticated()  # if every http method has to be authenticated
@api(
    URI='/hello',
    # SPECIFICATION_PATH='hello', # path for specification list
    # PREFIX=False, # if missing or True it will be on /prefix/hello
    )
class Hello(Base):

    # @authenticated()  # if get method has to be authenticated
    # @params(          # if you want to add params - uncomment method declaration also
    #     {'name': 'key', 'type': str, 'required': True,  'doc': 'option key',
    #           'default': 'key', 'min': 10, 'max': 20},
    # )
    # def get(self, key):
    def get(self):
        # return self.ok('hello get', key)
        return self.ok('hello get')

    # @authenticated()  # if put method has to be authenticated
    def put(self):
        return self.ok('hello put')

    # @authenticated()  # if post method has to be authenticated
    def post(self):
        return self.ok('hello post')

    # @authenticated()  # if patch method has to be authenticated
    def patch(self):
        return self.ok('hello patch')

    # @authenticated()  # if delete method has to be authenticated
    def delete(self):
        return self.ok('hello delete')
