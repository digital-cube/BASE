# try:
#     from setuptools import setup
# except ImportError:
#     from distutils.core import setup
import base
from distutils.core import setup

setup(
    name='base',
    version=base.__VERSION__,
    packages=['base',
              'base.application',
              'base.application.api',
              'base.application.api.user',
              'base.application.api.utils',
              'base.application.lookup',
              'base.application.helpers',
              'base.application.templates',
              'base.common',
              'base.config',
              'base.builder',
              'base.builder.project_additional',
              'base.builder.template_project',
              'base.builder.template_project.src',
              'base.builder.template_project.src.api',
              'base.builder.template_project.src.api_hooks',
              'base.builder.template_project.src.config',
              'base.builder.template_project.src.lookup',
              'base.builder.template_project.src.models',
              'base.builder.template_project.tests'],
    url='https://github.com/digital-cube/BASE',
    license='GNU',
    author='Digital Cube doo',
    author_email='slobodan@digitalcube.rs',
    description='Base, simple scaling project',
    install_requires=['tornado', 'bcrypt'],
    data_files=[('/usr/local/bin', ['base/bin/basemanager.py', 'base/bin/basemanager']), ],
    package_data={'base.application.templates': ['*'] },
)
