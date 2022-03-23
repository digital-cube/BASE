import os
#import base

VERSION = [3, 0, 0]
__VERSION__ = '.'.join(map(str, VERSION))

import platform
from setuptools import setup

_dir = os.path.dirname(__file__)

# read the contents of your README file
with open('README.rst') as f:
    long_description = f.read()

setup(
    name='base3imp',
    version=__VERSION__,
    packages=['base',
              'base.src',
              'base.src.base',
              'base.src.base.common',
              'base.src.base.config',
              'base.src.base.helpers',
              'base.src.base.utils',
              ],
    url='https://base3.dev',
    license='https://www.gnu.org/licenses/gpl-3.0.en.html',
    author='Digital Cube doo',
    author_email='info@digitalcube.rs',
    description='Base3',
    long_description=long_description,

    install_requires=['tornado',
                      'bcrypt',
                      'logfmt',
                      'python-dateutil',
                      'sendgrid',
                      'aiotask-context',
                      'alembic',
                      'bcrypt',
                      'psycopg2-binary',
                      'PyJWT',
                      'pyjwt-rsa',
                      'PyYAML',
                      'redis',
                      'requests',
                      'SQLAlchemy==1.3.23',
                      'aerich==0.5.8',
                      'tortoise-orm[asyncpg]',
#                      'tortoise-orm[accel]',
                      'aiomysql'
                      ],
    package_data={
        'base': [
            'src/base/config/config.example.yaml',
    ]}
)
