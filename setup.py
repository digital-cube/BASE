import os
from setuptools import setup

__VERSION__ = '3.0.7'


_dir = os.path.dirname(__file__)

# read the contents of your README file
with open('README.rst') as f:
    long_description = f.read()

setup(
    name='base3',
    version=__VERSION__,
    packages=['base',
              'base.src',
              'base.src.base',
              'base.src.base.common',
              'base.src.base.config',
              'base.src.base.helpers',
              'base.src.base.lookup',
              'base.src.base.utils',
              ],
    url='https://base3.dev',
    license='https://www.gnu.org/licenses/gpl-3.0.en.html',
    author='Digital Cube doo',
    author_email='info@digitalcube.rs',
    description='Base3',
    long_description=long_description,
    install_requires=[
        'aerich',
        'aiomysql',
        'aiotask-context',
        'asynctest',
        'bcrypt',
        'logfmt',
        'psycopg2-binary',
        'PyJWT',
        'pyjwt-rsa',
        'PyYAML',
        'python-dateutil',
        'redis',
        'requests',
        'tornado',
        'tortoise-orm[asyncpg]',
        'tortoise-orm[accel]',
    ],
    package_data={
        'base': [
            'src/base/config/config.yaml',
    ]},
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development"
    ],
)
