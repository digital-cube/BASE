import os
import sys
import json
import importlib

from base.application.lookup import exit_status
from base.builder.maker.common import update_path
from base.builder.maker.common import get_install_directory
from base.builder.maker.common import copy_dir
from base.builder.maker.common import copy_file
from base.common.orm import init_orm
from base.config.settings import models_config_file
from base.common.utils import check_slugify_library_installed
from base.common.utils import check_timeago_library_installed


def _add_modules_to_config(config_file):

    # edit application config file and add blog API
    with open(config_file, 'r') as cf:
        _file = cf.readlines()

    _new_file = []

    for _line in _file:

        if _line[:11] == 'imports = [':
            _new_file.append(_line)
            _new_file.append("    'src.api.blog.comments',\n")
            _new_file.append("    'src.api.blog.files',\n")
            _new_file.append("    'src.api.blog.posts',\n")
            _new_file.append("    'src.api.blog.tags',\n")
            continue

        _new_file.append(_line)

    with open(config_file, 'w') as cf:

        cf.write(''.join(_new_file))

    return True


def _add_tests(app_config):

    test_dir = os.path.abspath(os.path.join(os.path.dirname(app_config.__file__), '../../tests'))
    tests_file = '{}/start_all_tests.py'.format(test_dir)

    if os.path.isdir(test_dir) and os.path.isfile(tests_file):

        with open(tests_file, 'r') as tf:
            _file = tf.readlines()

        _new_file = []

        for _line in _file:

            if 'tests.hello' in _line:
                _new_file.append(_line)
                _new_file.append("from tests.blog_tests import TestBlog\n")
                _new_file.append("from tests.blog_tests import TestPostGroups\n")
                _new_file.append("from tests.blog_tests import TestPostTags\n")
                _new_file.append("from tests.blog_tests import TestFilesUpload\n")
                _new_file.append("from tests.blog_tests import TestUserGetPosts\n")
                _new_file.append("from tests.blog_tests import TestPostMeta\n")


                continue

            _new_file.append(_line)

        with open(tests_file, 'w') as tf:

            tf.write(''.join(_new_file))
    else:
        print('Please update tests with new blog_tests ')


def _update_sequencer_model(app_config):

    s_post_class = '''

class s_posts(base.common.orm.sql_base):
    __tablename__ = 's_posts'

    id = Column(CHAR(10), primary_key=True)
    active_stage = Column(CHAR(3), index=True, nullable=False)

    def __init__(self, _id, active_stage):
        self.id = _id
        self.active_stage = active_stage

'''
    sequencer_module_file = os.path.abspath(os.path.join(os.path.dirname(app_config.__file__), '../models/sequencers.py'))

    with open(sequencer_module_file) as sf:
        slines = sf.readlines()

    _new_file = []
    for _line in slines:

        if _line[:11] == 'def main():':
            _new_file.append(s_post_class)

        _new_file.append(_line)

    with open(sequencer_module_file, 'w') as sf:
        sf.write(''.join(_new_file))

    print('UPDATE')


def add_blog():

    # check if needed library are installed
    if not check_slugify_library_installed():
        print('''
        Missing slugify library, 
        please install: pip3 install python-slugify
        ''')
        return

    if not check_timeago_library_installed():
        print('''
        Missing timeago library, 
        please install: pip3 install timeago
        ''')
        return

    update_path()
    try:
        import src.config.app_config
    except ImportError as e:
        print('Can not find application configuration')
        sys.exit(exit_status.MISSING_PROJECT_CONFIGURATION)

    if not hasattr(src.config.app_config, 'db_config'):
        print('Missing Database configuration in config file, please initialize database first')
        sys.exit(exit_status.MISSING_DATABASE_CONFIGURATION)

    # check if config file has active models, and update models with blog models
    import src.config.app_config
    models_file = '{}/{}'.format(os.path.dirname(src.config.app_config.__file__), models_config_file)
    models_directory = '{}/{}'.format(os.path.abspath(os.path.join(os.path.dirname(src.config.app_config.__file__), '..')), 'models')

    if not os.path.isdir(models_directory) or \
            (not os.path.isfile(models_file) and not hasattr(src.config.app_config, 'models')):
                print('Models not initialized, please execute db_init first')
                sys.exit(exit_status.MISSING_DATABASE_CONFIGURATION)

    if not os.path.isfile(models_file) and hasattr(src.config.app_config, 'models'):
        print('Models defined in config file, please update models in application config file with new blog model')
    else:

        with open(models_file) as mf:
            models = json.load(mf)
        if any(list(map(lambda m: 'blog' in m, models))):
            print('Models should contain blog module, please check configuration')
        else:
            models.append('src.models.blog')
            with open(models_file, 'w') as mf:
                json.dump(models, mf, indent=4, sort_keys=True, ensure_ascii=False)

    # copy lookup for post statutes
    _site_dir = get_install_directory()
    _lookup_source = '{}/base/builder/project_additional/lookup/post_status.py'.format(_site_dir[0])
    _lookup_dest = 'src/lookup/post_status.py'
    copy_file(_lookup_source, _lookup_dest)

    # copy models for blog
    _destination_file = 'src/models/blog.py'
    models_additional_source_dir = '{}/base/builder/project_additional/models_additional'.format(_site_dir[0])
    models_file = '{}/blog.py'.format(models_additional_source_dir)
    copy_file(models_file, _destination_file)

    # update users model with posts
    print('Change users model, please check the users model for changes')
    os.remove('src/models/user.py')
    _user_with_blog_model = '{}/base/builder/project_additional/models_additional/user_with_blog.py'.format(_site_dir[0])
    copy_file(_user_with_blog_model, 'src/models/user.py')

    # create tables for blog
    orm_builder = init_orm()
    import base.common.orm
    setattr(base.common.orm, 'orm', orm_builder.orm())
    orm_builder.add_blog()
    try:
        _m = importlib.import_module('src.models.blog')
        _m.main()
    except ImportError:
        print('Error loading model {}, please execute the main manually'.format(src.models.blog.__file__))

    # check if api exists, if not copy it from the repo
    api_source_dir = '{}/base/builder/project_additional/api/blog'.format(_site_dir[0])
    common_source_dir = '{}/base/builder/project_additional/common'.format(_site_dir[0])
    config_source = '{}/base/builder/project_additional/config/blog_config.py'.format(_site_dir[0])

    copy_dir(api_source_dir, 'src/api/blog')
    copy_dir(common_source_dir, 'src/common')
    copy_file(config_source, 'src/config/blog_config.py')

    # update app config with api paths
    _add_modules_to_config(src.config.app_config.__file__)

    # add tests for blog
    test_source = '{}/base/builder/project_additional/tests/blog_tests.py'.format(_site_dir[0])
    test_file1 = '{}/base/builder/project_additional/tests/test_file.png'.format(_site_dir[0])
    test_file2 = '{}/base/builder/project_additional/tests/test_file2.pdf'.format(_site_dir[0])
    test_file3 = '{}/base/builder/project_additional/tests/test_file3.txt'.format(_site_dir[0])
    copy_file(test_source, 'tests/blog_tests.py')
    copy_file(test_file1, 'tests/test_file.png')
    copy_file(test_file2, 'tests/test_file2.pdf')
    copy_file(test_file3, 'tests/test_file3.txt')

    _add_tests(src.config.app_config)
    print('blog component is in the system')

