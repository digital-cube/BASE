import sys
import shutil

from base.application.lookup import exit_status
from base.builder.maker.common import get_install_directory
from base.config.settings import playground_usage


def create_playground(parsed_args):

    _playground = 'playground'

    _site_dir = get_install_directory()
    source_dir = '{}/base/builder/{}'.format(_site_dir[0], _playground)

    try:
        shutil.copytree(source_dir, _playground)
    except FileExistsError as e:
        print('Directory {} already exists, please rename/remove existing one'.format(_playground))
        sys.exit(exit_status.PROJECT_DIRECTORY_ALREADY_EXISTS)
    except PermissionError as e:
        print('Can not create {} directory, insufficient permissions'.format(_playground))
        sys.exit(exit_status.PROJECT_DIRECTORY_PERMISSION_ERROR)

    print(playground_usage)

