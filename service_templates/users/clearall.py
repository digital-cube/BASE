#!/usr/bin/env python
import os
import sys
import json
import base.orm
import importlib

import base.registry

def init(svc):
    importlib.import_module(f'orm.models')

    db_config = base.registry.db(svc)

    print('dbc',db_config)
    orm = base.orm.init_orm(db_config)
    orm.clear_database()
    orm.create_db_schema()


if __name__ == "__main__":
    init('users')
