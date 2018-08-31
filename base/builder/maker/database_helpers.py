import os
import sys
import json

from inspect import getmembers, isclass
from sqlalchemy.ext.declarative.api import DeclarativeMeta

from base.application.lookup import exit_status
from base.builder.maker.common import update_path
from base.builder.maker.common import get_orm_models
from base.common.orm import init_orm
from base.config.settings import db_init_warning
from base.config.settings import models_config_file


def show_create_table(args):

    update_path()

    src = 'src/config/app_config.py'
    if not os.path.isfile(src):
        print(db_init_warning)
        sys.exit(exit_status.MISSING_PROJECT_CONFIGURATION)

    import src.config.app_config
    models_file = '{}/{}'.format(os.path.dirname(src.config.app_config.__file__), models_config_file)
    if not os.path.isfile(models_file) and not hasattr(src.config.app_config, 'models'):
        print('Nothing to be done')
        return

    if not hasattr(src.config.app_config, 'db_config'):
        print('No database configuration in configuration file')
        sys.exit(exit_status.MISSING_DATABASE_CONFIGURATION)

    __dest_dir = os.path.dirname(src.config.app_config.__file__)
    __db_config_file = '{}/{}'.format(__dest_dir, src.config.app_config.db_config)

    with open(__db_config_file) as _db_cfg:
        try:
            db_config = json.load(_db_cfg)
        except json.JSONDecodeError:
            print('Can not load database configuration')
            sys.exit(exit_status.DATABASE_NOT_CONFIGURED)

    _models_modules = []
    get_orm_models(_models_modules, src.config.app_config)

    _port = str(src.config.app_config.port)
    if _port not in db_config:
        print('Missing database configuration for port: {}'.format(_port))
        sys.exit(exit_status.DATABASE_NOT_CONFIGURED)

    orm_builder = init_orm()

    # PREPARE DATABASE
    _orm_model = None
    for m in _models_modules:

        break1 = False
        for _name, _model in getmembers(m, isclass):
            if type(_model) == DeclarativeMeta and hasattr(_model, '__table__'):
                if _model.__table__.name == args.table_name:
                    _orm_model = _model
                    break1 = True
                    break
        if break1:
            break

    if _orm_model is None:
        print('Table {} has no model, or model not configured'.format(args.table_name))
        sys.exit(exit_status.TABLE_NOT_PRESENT)

    _db_engine = orm_builder.orm().engine()
    from sqlalchemy.schema import CreateTable
    _create_table_query = CreateTable(_orm_model.__table__).compile(_db_engine)
    print('{} table create query:\n'.format(args.table_name))
    print(_create_table_query)

