# try:
#     from setuptools import setup
# except ImportError:
#     from distutils.core import setup
import os
import base
import platform
from distutils.core import setup

__WINDOWS__ = platform.system() == 'Windows'

_scripts= [] if __WINDOWS__ else ['base/bin/basemanager.py', 'base/bin/basemanager']
_entry_points={
                 'console_scripts': [
                     'basemanager = base.bin.basemanager:execute_builder_cmd'
                 ]
             } if __WINDOWS__ else {}

_dir = os.path.dirname(__file__)
print('VOOA JE DIR', _dir)
setup(
    name='base',
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
              'base.tests',
              'base.tests.api',
              'base.tests.api.user',
              'base.tests.api.utils',
              'base.tests.application',
              'base.tests.helpers'
              ],
    url='https://github.com/digital-cube/BASE',
    license='GNU',
    author='Digital Cube doo',
    author_email='slobodan@digitalcube.rs',
    description='Base, simple scaling project',
    install_requires=['tornado', 'bcrypt'],
    entry_points=_entry_points,
    scripts=_scripts,
    package_data={
        'base': [
            'application/templates/*',
            'bin/*',
            'builder/playground/*',
            'builder/project_additional/*',
            'builder/project_additional/models/*',
            'builder/project_additional/api_hooks/*',
            'builder/template_project/*',
            'builder/template_project/src/*',
            'builder/template_project/src/api/*',
            'builder/template_project/src/config/*',
            'builder/template_project/src/lookup/*',
            'builder/template_project/static/img/*',
            'builder/template_project/tests/*',
        ],
    },
)
