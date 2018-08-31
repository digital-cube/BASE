# coding: utf-8

import sys
from base.application.lookup import exit_status


class DummyArgumentParser:

    application_port = None


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
        return
        # print("Missing database configuration, please check you config file")
        # sys.exit(exit_status.MISSING_DATABASE_CONFIGURATION)

    setattr(src.config.app_config, 'debug', False)

    import base.builder.maker.database_builder
    return base.builder.maker.database_builder.build_database(DummyArgumentParser(), test=True)

