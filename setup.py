# try:
#     from setuptools import setup
# except ImportError:
#     from distutils.core import setup
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
              'base.application.templates',
              'base.common',
              'base.config',
              'base.builder',
              'base.builder.playground',
              'base.builder.project_additional',
              'base.builder.template_project',
              'base.builder.template_project.log',
              'base.builder.template_project.src',
              'base.builder.template_project.src.api',
              'base.builder.template_project.src.api_hooks',
              'base.builder.template_project.src.config',
              'base.builder.template_project.src.lookup',
              'base.builder.template_project.src.models',
              'base.builder.template_project.tests',
              'base.tests',
              'base.tests.api',
              'base.tests.api.user',
              'base.tests.api.utils',
              'base.tests.application',
              'base.tests.helpers',
              'base.bin',
              ],
    url='https://github.com/digital-cube/BASE',
    license='GNU',
    author='Digital Cube doo',
    author_email='slobodan@digitalcube.rs',
    description='Base, simple scaling project',
    install_requires=['tornado', 'bcrypt'],
    entry_points=_entry_points,
    scripts=_scripts,
    package_data={'base.application.templates': ['*'], 'base.builder.playground': ['*']},
)
