# coding= utf-8

"""
Register or login a user with his facebook account access token
provided from the client application.
A client application is responsible for getting an access token.
"""

import json
import tornado
import tornado.gen
import tornado.ioloop
import tornado.concurrent

import base.application.lookup.responses as msgs
from base.application.components import api
from base.application.components import params
from base.common.utils import log
from base.common.utils import check_facepy_library_installed
from base.application.api.user.gaccess import SocialAccess


@api(
    URI='/user/f-access',
    PREFIX=False,
    SPECIFICATION_PATH='User')
class FAccess(SocialAccess):

    # facebook_user = None
    provider = 'facebook'
    facebook_user_path = '/me?fields=id,name,email,about,first_name,gender,last_name'

    @params(
        {'name': 'user', 'type': json, 'required': True,  'doc': 'facebook user'},
    )
    @tornado.gen.coroutine
    def post(self, facebook_user):
        """Register/login user with facebook access token"""

        if not check_facepy_library_installed():
            log.error('Library for Facebook API is not installed, can not continue for user: {}'.format(facebook_user))
            return self.error(msgs.FACEBOOK_LIBRARY_NOT_INSTALLED)

        self.social_user = facebook_user

        if not self.check_facebook_user():
            log.error('Wrong user structure: {}'.format(facebook_user))
            return self.error(msgs.FACEBOOK_USER_INVALID)

        # get data for user
        if tornado.version >= '5.0':
            user_verified = yield tornado.ioloop.IOLoop.current().run_in_executor(None, self.get_user_info)
        else:
            th_executor = tornado.concurrent.futures.ThreadPoolExecutor(4)
            user_verified = yield th_executor.submit(self.get_user_info)

        if not user_verified:
            log.warning('Error verify facebook user')
            return self.error(msgs.ERROR_GET_FACEBOOK_USER)

        # register user if not already registered
        # get session token
        # return user's data and session token
        if tornado.version >= '5.0':
            response = yield tornado.ioloop.IOLoop.current().run_in_executor(None, self.log_user_in)
        else:
            th_executor = tornado.concurrent.futures.ThreadPoolExecutor(4)
            response = yield th_executor.submit(self.log_user_in)

        if not response:
            log.warning('Error in login/register facebook user {}'.format(self.social_user['email']))
            return self.error(msgs.ERROR_AUTHORIZE_FACEBOOK_USER)

        self.set_authorized_cookie(response)
        self.ok(response)

    def check_facebook_user(self):

        user_fields = ["id", "email", "image", "name", "provider", "token"]
        for f in user_fields:
            if f not in self.social_user:
                log.error('Missing {} in facebook user: {}'.format(f, self.social_user))
                return False

        if self.social_user['provider'] != self.provider:
            log.error('Invalid provider {} for facebook user: {}'.format(self.social_user['provider'], self.social_user))
            return False

        return True

    def get_user_info(self):
        """
        Fetch the user from the facebook's account
        with GraphQL path '/me?fields=id,name,email,about,first_name,gender,last_name'
        User model:
         'id': '__facebook_user_id__',
         'name': '__facebook_user_full_name__',
         'email': '__facebook_user_email__',
         'first_name': '__facebook_user_first_name__',
         'gender': '__facebook_user_gender__',
         'last_name': '__facebook_user_last_name__',
         'headers': {
            'ETag': '"xxxx"',
            'Strict-Transport-Security': 'xxxx',
            'x-fb-trace-id': 'xxxx',
            'x-fb-rev': 'xxx',
            'x-app-usage':'{}',
            'Expires': 'Sat, 01 Jan 2000 00:00:00 GMT',
            'Content-Type': 'application/json; charset=UTF-8',
            'facebook-api-version': 'vx.x',
            'Cache-Control': 'private, no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Access-Control-Allow-Origin': '*',
            'Vary': 'Accept-Encoding',
            'Content-Encoding': 'gzip',
            'X-FB-Debug': 'xxx'
            'Date': 'Sat, 01 Jan 2000 00:00:00 GMT',
            'Connection': 'keep-alive',
            'Content-Length': '130'}}
        }

        :return: bool - user fetched
        """

        import facepy.exceptions
        try:
            facebook_graph = facepy.GraphAPI(self.social_user['token'])
            facebook_user = facebook_graph.get(self.facebook_user_path)
        except facepy.exceptions.OAuthError:
            log.critical('Token for user {} is invalid'.format(self.social_user))
            return False
        except facepy.exceptions.FacebookError:
            log.critical('Error in user info request for user: {}'.format(self.social_user))
            return False
        self.social_user.update(facebook_user)

        return True

