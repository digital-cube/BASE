# coding= utf-8
import datetime
from sqlalchemy import Column, ForeignKey, Boolean, DateTime, SmallInteger, CHAR
import base.common.orm
import base.application.lookup.session_token_type as token_type


class SessionTokens(base.common.orm.sql_base):

    __tablename__ = 'session_tokens'

    id = Column(CHAR(64), primary_key=True)
    id_user = Column(CHAR(10), ForeignKey('auth_users.id'), nullable=False)
    active = Column(Boolean, index=True, nullable=False, default=True)
    type = Column(SmallInteger, index=True, nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    expired = Column(DateTime)
    last_used = Column(DateTime, nullable=False, default=datetime.datetime.now)

    def __init__(self, _id, id_user, active=True, type=token_type.SIMPLE, expired=None):

        self.id = _id
        self.id_user = id_user
        self.active = active
        self.type = type
        self.expired = expired


def main():
    pass

if __name__ == '__main__':

    main()

