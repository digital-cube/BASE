import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime, Text
import common.orm


class AuthUser(common.orm.sql_base):

    __tablename__ = 'auth_users'

    id = Column(String(10), primary_key=True)
    username = Column(String(64), index=True, nullable=False, unique=True)
    password = Column(String(64), nullable=False)
    role_flags = Column(Integer, index=True, nullable=False)
    active = Column(Boolean, index=True, nullable=False, default=False)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now())

    def __init__(self, _id, username, password, role_flags=1, active=False):

        self.id = _id
        self.username = username
        self.password = password
        self.role_flags = role_flags
        self.active = active
        self.created = datetime.datetime.now()


class User(common.orm.sql_base):

    __tablename__ = 'users'

    id = Column(String(10), ForeignKey(AuthUser.id), primary_key=True)
    first_name = Column(String(64), index=True)
    last_name = Column(String(64))
    data = Column(Text)

    def __init__(self, id_user, first_name, last_name, data):

        self.id = id_user
        self.first_name = first_name
        self.last_name = last_name
        self.data = data


def main():
    pass

if __name__ == '__main__':

    main()
