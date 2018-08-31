import sys

from base.application.lookup import exit_status
from base.builder.maker.common import update_path
from base.config.settings import available_BASE_components


def _add_blog():

    update_path()
    try:
        import src.config.app_config
    except ImportError as e:
        print('Can not find application configuration')
        sys.exit(exit_status.MISSING_PROJECT_CONFIGURATION)

    if not hasattr(src.config.app_config, 'db_config'):
        print('Missing Database configuration in config file')
        sys.exit(exit_status.MISSING_DATABASE_CONFIGURATION)

    # check if config file has active models, and update models with blog models
    # check if models are presented if not copy them
    # create tables for blog (https://stackoverflow.com/questions/41030566/sqlalchemy-add-a-table-to-an-already-existing-database)
    #   orm has to bi initialized
    #   model_name.__table__.create(db_session.bind)
    # check if api exists, if not copy it from the repo
    # update app config with api paths

    print('blog added to the system')


def add_component(parsed_args):

    if parsed_args.component not in available_BASE_components:
        print('''
        Component "{}" not recognized,
        please use 'db_init list' to see available components
        '''.format(parsed_args.component))
        sys.exit(exit_status.BASE_COMPONENT_NOT_EXISTS)

    if parsed_args.component == 'blog':
        _add_blog()


def list_components(parsed_args):
    msg = '''
    available components: {}
    '''.format(''.join(['\n\t{}'.format(c) for c in available_BASE_components]))
    print(msg)

