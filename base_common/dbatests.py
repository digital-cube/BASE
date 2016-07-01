# -*- coding: utf-8 -*-

import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from base_svc.comm import call
from base_api.users.user_login import location as login_location
from base_config.settings import TEST_USER, TEST_USER_PWD


def test_authorize(svc_url, svc_port, username=None, password=None, force_json=False):
    """
    Authorization API for tests
    :param svc_url: base API domain (localhost)
    :param svc_port: base API port, int
    :param username: defined or chosen username
    :param password: defined or chosen password
    :param force_json: force json return type
    :return: request response or json
    """

    data = {
        'username': username if username else TEST_USER,
        'password': password if password else TEST_USER_PWD
    }

    res, status = call(svc_url, svc_port, login_location, data, 'POST')

    if force_json:
        return res, status

    res = json.loads(res)
    if status < 300:
        return res['token'], status

    return res['message'], status

