# coding= utf-8

from base.application.components import Base
from base.application.components import api
from base.application.components import params
from src.models.utils import Options as OrmOptions
import base.common.orm
from base.common.utils import log


@api(
    URI='/option/:key',
    PREFIX=False)
class Options(Base):

    @params(
        {'name': 'key', 'type': str, 'required': True,  'doc': 'option key'},
    )
    def get(self, _key):

        _q = base.common.orm.orm.session().query(OrmOptions).filter(OrmOptions.key == _key)

        if _q.count() != 1:
            log.warning('Missing option {}{}'.format(
                _key, ' or {} occurrences found'.format(_q.count() if _q.count() != 0 else '')))
            return self.error("Missing option '{}'".format(_key))   # TODO: make res messages return

        _option = _q.one()

        return self.ok({_option.key: _option.value})

    @params(
        {'name': 'key', 'type': str, 'required': True,  'doc': 'option key'},
        {'name': 'value', 'type': str, 'required': True,  'doc': 'option value'},
    )
    def put(self, _key, _value):

        _session = base.common.orm.orm.session()
        _q = _session.query(OrmOptions).filter(OrmOptions.key == _key)

        if _q.count() == 1:

            _option = _q.one()
            _option.value = _value

        elif _q.count() == 0:

            _option = OrmOptions(_key, _value)
            _session.add(_option)

        else:
            log.warning('Found {} occurrences for {}'.format(_q.count(), _key))
            return self.error('To many values for {}'.format(_key)) # TODO: change to res messages

        _session.commit()

        return self.ok({_option.key: _option.value})
