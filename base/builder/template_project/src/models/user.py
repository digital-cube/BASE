import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime, Text
import common.orm


class AuthUser(common.orm.sql_base):

    __tablename__ = 'auth_users'

    id = Column(String(10), primary_key=True)
    username = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    role_flags = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, default=False)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now())

    def __init__(self, username, password, role_flags):

        self.username = username
        self.password = password
        self.role_flags = role_flags


class User(common.orm.sql_base):

    __tablename__ = 'users'

    id = Column(String(10), ForeignKey(AuthUser.id), primary_key=True)
    first_name = Column(String(64))
    last_name = Column(String(64))
    data = Column(Text)

    def __init__(self, id_user):

        self.id = id_user

    def set_first_name(self, first_name):
        self.first_name = first_name

    def set_last_name(self, last_name):
        self.last_name = last_name

    def set_data(self, data):
        self.data = data


def main():
    pass

if __name__ == '__main__':

    main()
