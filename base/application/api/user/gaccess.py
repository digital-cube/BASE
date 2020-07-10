# coding= utf-8

"""
Register or login a user with his google account access token
provided from the client application.
A client application is responsible for getting an access token.
An application has to be configured with the google application client id
"""

import json
import time
import uuid
import requests
import tornado
import tornado.gen
import tornado.ioloop
import tornado.concurrent

import base.application.lookup.responses as msgs
from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.common.utils import log
from base.common.utils import user_exists
from base.common.utils import get_google_discovery_docs
from base.common.utils import set_google_discovery_docs


class SocialAccess(Base):

    social_user = None

    def log_user_in(self):
        """
        Register or login user
        :return:  bool - if something wrong, or dict with the response
        """

        import base.common.orm
        from base.common.tokens_services import get_token
        from base.application.api_hooks import api_hooks

        AuthUsers = base.common.orm.get_orm_model('auth_users')
        with base.common.orm.orm_session() as _session:

            response = {}
            _user = user_exists(self.social_user['email'], AuthUsers, _session, as_bool=False)
            if _user:
                # user exists - log in the user
                id_user = _user.id
                log.info('User {} already exists, login the user'.format(self.social_user['email']))
                _token = get_token(_user.id, {})
                if not _token:
                    log.critical('Error getting token for user {} - {}'.format(_user.id, _user.username))
                    return False

                response.update(_token)

            else:
                # user do not exists - register user
                from base.common.sequencer import sequencer
                id_user = sequencer().new('u', session=_session)

                if not id_user:
                    log.error('Can not create id for new user: {}'.format(self.social_user['email']))
                    return False

                _password = uuid.uuid4()
                _user_registered = api_hooks.register_user(id_user, self.social_user['email'], _password, self.social_user)
                if _user_registered is None:
                    log.critical('Error register user {} with password {} and data {}'.format(
                        self.social_user['email'], _password, self.social_user))
                    return False

                if isinstance(_user_registered, dict):
                    response.update(_user_registered)
                elif _user_registered != True:
                    try:
                        response['message'] = str(_user_registered)
                    except Exception:
                        log.error('Can not make string from user register response')

                _token = get_token(id_user, {})
                if not _token:
                    log.critical('Error getting token for new user {} - {}'.format(id_user, self.social_user['email']))
                    return False
                response.update(_token)

                if hasattr(api_hooks, 'post_register_process'):
                    _post_register_result = api_hooks.post_register_process(
                        id_user, self.social_user['email'], _password, self.social_user, _token)
                    if not _post_register_result:
                        log.critical('Post register process error for user {} - {}'.format(
                            id_user, self.social_user['email']))
                        return False

                    if isinstance(_post_register_result, dict):
                        response.update(_post_register_result)

            if hasattr(api_hooks, 'post_social_login_process'):
                _post_social_login_result = api_hooks.post_social_login_process(id_user, self.social_user)
                if not _post_social_login_result:
                    log.critical('Post social login process error for user {} - {}'.format(
                        id_user, self.social_user['email']))
                    return False

                if isinstance(_post_social_login_result, dict):
                    response.update(_post_social_login_result)

        return response


@api(
    URI='/user/g-access',
    PREFIX=False,
    SPECIFICATION_PATH='User')
class GAccess(SocialAccess):

    GOOGLE_URLS = None
    access_token = None
    social_user = None
    auth_data = None

    @params(
        {'name': 'token', 'type': str, 'required': True,  'doc': 'access token'},
        {'name': 'auth_data', 'type': json, 'required': False, 'doc': 'additional data'},
    )
    @tornado.gen.coroutine
    def post(self, token, auth_data):
        """Register/login user with google access token"""

        import base.config.application_config

        if base.config.application_config.google_client_ID is None:
            log.warning('Missing google client id in the configuration file, can not continue')
            return self.error(msgs.MISSING_GACCESS_CONFIGURATION)

        # check that app is configured for google access
        if tornado.version >= '5.0':
            is_configured = yield tornado.ioloop.IOLoop.current().run_in_executor(None, self.is_configured)
        else:
            th_executor = tornado.concurrent.futures.ThreadPoolExecutor(4)
            is_configured = yield th_executor.submit(self.is_configured)

        if not is_configured:
            log.warning('Error reading google access configuration')
            return self.error(msgs.ERROR_READ_GACCESS_CONFIGURATION)

        # check the access token on google's side
        self.access_token = token
        self.auth_data = auth_data
        if tornado.version >= '5.0':
            token_verified = yield tornado.ioloop.IOLoop.current().run_in_executor(None, self.verify_token)
        else:
            th_executor = tornado.concurrent.futures.ThreadPoolExecutor(4)
            token_verified = yield th_executor.submit(self.verify_token)

        if not token_verified:
            log.warning('Error verify google access token')
            return self.error(msgs.ERROR_VERIFY_GOOGLE_ACCESS_TOKEN)

        # get data for user
        if tornado.version >= '5.0':
            user_verified = yield tornado.ioloop.IOLoop.current().run_in_executor(None, self.get_user_info)
        else:
            th_executor = tornado.concurrent.futures.ThreadPoolExecutor(4)
            user_verified = yield th_executor.submit(self.get_user_info)

        if not user_verified:
            log.warning('Error verify google user')
            return self.error(msgs.ERROR_GET_GOOGLE_USER)

        # register user if not already registered
        # get session token
        # return user's data and session token
        if tornado.version >= '5.0':
            response = yield tornado.ioloop.IOLoop.current().run_in_executor(None, self.log_user_in)
        else:
            th_executor = tornado.concurrent.futures.ThreadPoolExecutor(4)
            response = yield th_executor.submit(self.log_user_in)

        if not response:
            log.warning('Error in login/register google user {}'.format(self.social_user['email']))
            return self.error(msgs.ERROR_AUTHORIZE_GOOGLE_USER)

        self.set_authorized_cookie(response)
        self.ok(response)

    def is_configured(self):
        """
        Check if the configuration for the access and google's api urls are present
        :return: bool - configuration is valid
        """

        if self.GOOGLE_URLS is None:
            import base.config.application_config
            response = requests.get(base.config.application_config.google_discovery_docs_url)

            try:
                response = json.loads(response.text)
            except json.JSONDecodeError as e:
                log.critical('Error load google discovery docs: {}'.format(e))
                return False

            set_google_discovery_docs(response)

        self.GOOGLE_URLS = get_google_discovery_docs()

        log.info('Configuration for google access presented')
        return True

    def verify_token(self):
        """
        Token info model:
            {
                'azp': '__APP_CLIENT_ID__',
                'aud': '__APP_CLIENT_ID__',
                'sub': '__google_user_id__',
                'scope': 'https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email',
                'exp': '1532706115',
                'expires_in': '2922',
                'email': '__google_user_email__',
                'email_verified': 'true',
                'access_type': 'offline'
             }

        :return: bool - is verified
        """

        # self.GOOGLE_URLS['token_endpoint'] should be used for token verification, but there is a code that is missing
        from base.application.api_hooks import api_hooks
        import base.config.application_config
        params = {'access_token': self.access_token}
        response = requests.get(base.config.application_config.google_check_access_token_url, params=params)
        if response.status_code != 200:
            log.critical('Error fetch google token data: {}'.format(response.text))
            return False

        try:
            response = json.loads(response.text)
        except json.JSONDecodeError as e:
            log.critical('Error load google token verification response: {}'.format(e))
            return False

        if 'aud' not in response:
            log.critical('Missing audience for google access token: {}: {}'.format(self.access_token, response))
            return False
        if response['aud'] != api_hooks.get_google_authorized_client_id(self.auth_data):
            log.critical('Google access token audience is not valid: {}'.format(response))
            return False
        if 'exp' not in response:
            log.critical('Missing expiration date in google access token: {}'.format(response))
            return False
        try:
            exp = int(response['exp'])
        except Exception as e:
            log.critical('Error load google access token expiration time: {}'.format(response['exp']))
            return False
        if time.time() > exp:
            log.critical('Google access token expired: {}'.format(response))
            return False
        if 'email_verified' not in response or response['email_verified'] != 'true':
            log.critical('Email for users token not verified: {}'.format(response))
            return False

        log.info('Token for {} verified'.format(response['email']))
        return True

    def get_user_info(self):
        """
        Fetch the user from the google's account
        User mode:
         {
            "sub": "__google_user_id__",
            "name": "__google_user_first_and_last_name___",
            "given_name": "__google_user_first_name__",
            "family_name": "__google_user_last_name__",
            "profile": "__google_user_profile_public_address__",
            "picture": "__google_user_profile_picture_address__",
            "email": "__google_user_email__",
            "email_verified": true,
            "gender": "__google_user_gender__",
            "locale": "en"
        }

        :return: bool - user fetched
        """

        get_user_url = self.GOOGLE_URLS['userinfo_endpoint']
        params = {'access_token': self.access_token}
        response = requests.get(get_user_url, params=params)

        if response.status_code != 200:
            log.critical('Error fetch google user info: {}'.format(response.text))
            return False
        try:
            self.social_user = json.loads(response.text)
            self.social_user['first_name'] = self.social_user['given_name']
            self.social_user['last_name'] = self.social_user['family_name']
        except json.JSONDecodeError as e:
            log.critical('Error load google user info response: {}'.format(e))
            return False

        return True

