import json
import base.registry
from base import http
import redis
import datetime

from base import Base

from tornado.httpclient import AsyncHTTPClient

from orm.orm import orm_session
import orm.models as models


@Base.route(URI="/about")
class AboutUserServiceHandler(Base.BASE):

    @Base.api()
    async def get(self):
        return {'service': 'users'}


@Base.route(URI="/for_users/:ids")
class GetUsersInfoForListOfIdsHandler(Base.BASE):

    @Base.api()
    async def get(self, users_ids: str):
        res = {}
        for user in self.orm_session.query(models.User).filter(models.User.id.in_(users_ids.split(','))).all():
            res[user.id] = {'displayname': user.displayname(),
                            'username': user.username,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            }
        return res


@Base.route(URI="")
class UserHandler(Base.BASE):

    @Base.api()
    async def get(self):
        with orm_session() as sess:
            c = sess.query(models.User).count()

        return {'count': c}

    @Base.api()
    async def put(self, user: models.User):
        with orm_session() as sess:
            sess.add(user)
            sess.commit()

            return {'id': user.id}, http.code.HTTPStatus.CREATED


@Base.route(URI="/register")
class UserRegisterHandler(Base.BASE):

    @Base.api()
    async def post(self, username: str, password: str):
        with orm_session() as sess:
            user = models.User(username, password, role_flags=0)
            sess.add(user)
            sess.commit()

            return {'id': user.id}, http.code.HTTPStatus.CREATED


@Base.route(URI="/sessions")
class SessionsHandler(Base.BASE):

    @Base.auth()
    @Base.api()
    async def get(self):
        return {"id_user": self.id_user}

    @Base.auth()
    @Base.api()
    async def delete(self):
        with orm_session() as _orm_session:
            s = _orm_session.query(models.Session).filter(models.Session.id == self.id_session).one_or_none()
            s.active = False
            s.closed = datetime.datetime.now()
            r = redis.Redis()
            r.set(self.id_session, 0)

        return None

    @Base.api()
    async def put(self, username: str, password: str):
        with orm_session() as _orm_session:
            user = _orm_session.query(models.User).filter(models.User.username == username,
                                                          models.User.password == password).one_or_none()
            if not user:
                raise http.HttpErrorUnauthorized

            token = models.Session(user)
            _orm_session.add(token)
            _orm_session.commit()

            r = redis.Redis()
            r.set(token.id, 1)

            return {'token': token.jwt}, http.code.HTTPStatus.CREATED

        raise http.General4xx
