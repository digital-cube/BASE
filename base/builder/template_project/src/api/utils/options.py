# coding= utf-8

import base.common.orm
from base.common.utils import log
from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.application.components import authenticated

import src.lookup.response_messages as msgs
from src.models.utils import Options as OrmOptions


@authenticated()
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
            return self.error(msgs.MISSING_OPTION, option=_key)

        _option = _q.one()

        return self.ok({_option.key: _option.value})

    @params(
        {'name': 'key', 'type': str, 'required': True,  'doc': 'option key'},
        {'name': 'value', 'type': str, 'required': True,  'doc': 'option value'},
    )
    def put(self, _key, _value):


        _user =
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
            return self.error(msgs.OPTION_MISMATCH, option=_key)

        log.info('User {} set option {} -> {}'.format('username', _key, _valuea))
        _session.commit()

        return self.ok({_option.key: _option.value})
