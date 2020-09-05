import contextlib
import base.orm
import base.registry

db_config = base.registry.db('users')


def session():
    if not base.orm._orm or db_config['database'] not in base.orm._orm:
        base.orm.activate_orm(db_config)

    _session = base.orm._orm[db_config['database']].session()

    return _session


@contextlib.contextmanager
def orm_session():
    if not base.orm._orm or db_config['database'] not in base.orm._orm:
        base.orm.activate_orm(db_config)

    _session = base.orm._orm[db_config['database']].session()
    try:
        yield _session
    except Exception as e:
        print("E",e)
        _session.rollback()
        _session.close()
        raise
    finally:
        _session.close()
