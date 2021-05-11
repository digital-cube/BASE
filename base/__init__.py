"""
BASE3 Module
"""

VERSION = [3, 0, 7]
__VERSION__ = '.'.join(map(str, VERSION))

from .src.base import app
from .src.base import exceptions
from .src.base import http
from .src.base import orm
from .src.base import registry
from .src.base import store
from .src.base import test
from .src.base import token
from .src.base.app import Base
from .src.base.app import api
from .src.base.app import auth
from .src.base.app import api_auth
from .src.base.app import route
from .src.base.app import run
from .src.base.app import make_app
from .src.base.utils import sync_order
from .src.base.utils import ipc

from .src.base.config.config import config

from .src.base.helpers.paginator import paginate

from .src.base.helpers import common

from .src.base.lookup import scope_permissions
