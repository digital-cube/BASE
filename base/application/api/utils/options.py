# coding= utf-8

import base.common.orm
from base.common.utils import log
from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.application.components import authenticated

import base.application.lookup.responses as msgs


def save_option(key, value, orm_session=None):

    import base.common.orm
    OrmOptions = base.common.orm.get_orm_model('options')
    from base.common.utils import log
    with base.common.orm.orm_session() as _session:

        if orm_session:
            _session = orm_session

        _q = _session.query(OrmOptions).filter(OrmOptions.key == key)

        if _q.count() == 1:
            _option = _q.one()
            _option.value = value

        elif _q.count() == 0:
            _option = OrmOptions(key, value)
            _session.add(_option)

        else:
            log.warning('Found {} occurrences for {}'.format(_q.count(), key))
            return False

    return _option


@authenticated()
@api(
    URI='/tools/option/:key',
    PREFIX=False)
class Options(Base):

    @params(
        {'name': 'key', 'type': str, 'required': True,  'doc': 'option key'},
    )
    def get(self, _key):
        """Get option"""

        from base.common.utils import log
        OrmOptions = base.common.orm.get_orm_model('options')

        _q = self.orm_session.query(OrmOptions).filter(OrmOptions.key == _key)

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
        """Save option"""

        from base.common.utils import log
        _option = save_option(_key, _value, orm_session=self.orm_session)
        if not _option:
            return self.error(msgs.OPTION_MISMATCH, option=_key)

        log.info('User {} set option {} -> {}'.format('username', _key, _value))
        self.orm_session.commit()

        return self.ok({_option.key: _option.value})
