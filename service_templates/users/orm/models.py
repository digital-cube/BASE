from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from base.orm import sql_base, BaseSql
from sqlalchemy import Text

import base.exceptions as exceptions

import os
import jwt
import uuid
import datetime
import sqlalchemy
from jwt_rsa.rsa import generate_rsa
from cryptography.hazmat.primitives import serialization

current_file_folder = os.path.dirname(os.path.realpath(__file__))


class AuthUser(BaseSql, sql_base):
    __tablename__ = 'auth_users'

    id = Column(UUID, primary_key=True)
    username = Column(String(128), nullable=False, unique=True)
    password = Column(String(128), nullable=False)
    role_flags = Column(BigInteger, nullable=False)

    def __init__(self, username, password, role_flags):
        super(AuthUser, self).__init__()
        self.username = username
        self.password = password
        self.role_flags = role_flags


class User(AuthUser):
    __tablename__ = 'users'

    id = Column(ForeignKey('auth_users.id'), primary_key=True)
    email = Column(String(128))
    first_name = Column(String(128))
    last_name = Column(String(128))
    data = Column(JSONB(astext_type=Text()))

    def displayname(self):
        return self.username

    def __init__(self, username, password, role_flags=0, first_name=None, last_name=None, email=None):
        super(User, self).__init__(username, password, role_flags)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email




class Session(BaseSql, sql_base):
    __tablename__ = 'sessions'

    id = Column(UUID, primary_key=True)
    id_user = Column(ForeignKey('users.id'), nullable=False, index=True)
    ttl = Column(Integer)
    active = Column(Boolean, index=True)
    closed = Column(DateTime)
    user = relationship('User')

    def __init__(self, user, ttl=None, active=True):
        super(Session, self).__init__()

        self.user = user
        self.ttl = ttl
        self.active = active

        payload = {
            'id': self.id,
            'created': int(self.created.timestamp()),
            'expires': int((self.created + datetime.timedelta(seconds=self.ttl)).timestamp()) if self.ttl else None,
            'id_user': self.user.id,
        }

        from base.registry import private_key

        encoded = jwt.encode(payload, private_key(), algorithm='RS256')

        # this attribute will not be saved to DB
        self.jwt = encoded.decode('ascii')