# coding= utf-8
import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime, Text, CHAR
from sqlalchemy.orm import relationship
import base.common.orm


class AuthUser(base.common.orm.sql_base):

    __tablename__ = 'auth_users'

    id = Column(CHAR(10), primary_key=True)
    username = Column(String(64), index=True, nullable=False, unique=True)
    password = Column(String(64), nullable=False)
    role_flags = Column(Integer, index=True, nullable=False)
    active = Column(Boolean, index=True, nullable=False, default=False)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    user = relationship('User', uselist=False, back_populates='auth_user')

    def __init__(self, _id, username, password, role_flags=1, active=False):

        self.id = _id
        self.username = username
        self.password = password
        self.role_flags = role_flags
        self.active = active


class User(base.common.orm.sql_base):

    __tablename__ = 'users'

    id = Column(CHAR(10), ForeignKey(AuthUser.id), primary_key=True)
    first_name = Column(String(64))
    last_name = Column(String(64))
    auth_user = relationship("AuthUser", back_populates="user")

    def __init__(self, id_user, first_name, last_name):

        self.id = id_user
        self.first_name = first_name
        self.last_name = last_name


def main():
    pass


if __name__ == '__main__':

    main()
