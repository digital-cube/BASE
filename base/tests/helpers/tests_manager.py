# coding: utf-8

import sys
from base.application.lookup import exit_status


def prepare_test_database():
    """
    Prepare database for testing purposes. Find connection parameters from project's config.
    :return: void
    """

    try:
        import src.config.app_config
        import src.config.app_config as app_config
    except ImportError:
        print("Can not find project's configuration file, can not configure database exiting...")
        sys.exit(exit_status.MISSING_PROJECT_CONFIGURATION)

    if not hasattr(app_config, 'db_config'):
        print("Missing database configuration, please check you config file")
        sys.exit(exit_status.MISSING_DATABASE_CONFIGURATION)

    if not hasattr(app_config, 'db_type'):
        print("Missing database type, please check you config file")
        sys.exit(exit_status.MISSING_DATABASE_TYPE)

    # app_config.db_config['db_name'] = 'test_{}'.format(app_config.db_config['db_name'])
    setattr(src.config.app_config, 'debug', False)

    import base.builder.project_maker
    return base.builder.project_maker._build_database({}, test=True)

