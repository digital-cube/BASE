import os
import base
import platform
from setuptools import setup

__WINDOWS__ = platform.system() == 'Windows'

_scripts= [] if __WINDOWS__ else ['base/bin/basemanager.py', 'base/bin/basemanager']
_entry_points={
                 'console_scripts': [
                     'basemanager = base.bin.basemanager:execute_builder_cmd'
                 ]
             } if __WINDOWS__ else {}

_dir = os.path.dirname(__file__)

# read the contents of your README file
with open('README.rst') as f:
    long_description = f.read()

setup(
    name='dcbase',
    version=base.__VERSION__,
    packages=['base',
              'base.application',
              'base.application.api',
              'base.application.api.user',
              'base.application.api.utils',
              'base.application.api_hooks',
              'base.application.lookup',
              'base.application.helpers',
              'base.common',
              'base.config',
              'base.builder',
              'base.builder.maker',
              'base.builder.maker.components',
              'base.tests',
              'base.tests.api',
              'base.tests.api.user',
              'base.tests.api.utils',
              'base.tests.application',
              'base.tests.helpers'
              ],
    url='https://github.com/digital-cube/BASE',
    license='https://www.gnu.org/licenses/gpl-3.0.en.html',
    author='Digital Cube doo',
    author_email='info@digitalcube.rs',
    description='Base, simple scaling project',
    long_description=long_description,
    install_requires=['tornado', 'bcrypt', 'sendgrid'],
    entry_points=_entry_points,
    scripts=_scripts,
    package_data={
        'base': [
            'application/templates/*',
            'bin/*',
            'builder/playground/*',
            'builder/project_additional/*',
            'builder/project_additional/api/*',
            'builder/project_additional/api/blog/*',
            'builder/project_additional/api/site/*',
            'builder/project_additional/api_hooks/*',
            'builder/project_additional/common/*',
            'builder/project_additional/config/*',
            'builder/project_additional/db/*',
            'builder/project_additional/db/alembic/*',
            'builder/project_additional/db/alembic/versions/.gtkeep*',
            'builder/project_additional/lookup/*',
            'builder/project_additional/models/*',
            'builder/project_additional/models_additional/*',
            'builder/project_additional/tests/*',
            'builder/template_project/.gitignore',
            'builder/template_project/*',
            'builder/template_project/src/*',
            'builder/template_project/src/api/*',
            'builder/template_project/src/config/*',
            'builder/template_project/src/lookup/*',
            'builder/template_project/static/img/*',
            'builder/template_project/tests/*',
            'tests/helpers/pg_check.sh',
        ],
    },
)
