import datetime
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, SmallInteger
import common.orm


class SessionTokens(common.orm.sql_base):

    __tablename__ = 'session_token'

    id = Column(String(64), primary_key=True)
    id_user = Column(String(10), ForeignKey('auth_users.id'), nullable=False)
    active = Column(Boolean, index=True, nullable=False, default=True)
    type = Column(SmallInteger, index=True, nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now())
    expired = Column(DateTime)

    def __init__(self, _id, username, password, role_flags=1, active=False):

        self.id = _id
        self.username = username
        self.password = password
        self.role_flags = role_flags
        self.active = active
        self.created = datetime.datetime.now()


def main():
    pass

if __name__ == '__main__':

    main()

