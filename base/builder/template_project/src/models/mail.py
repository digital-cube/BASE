import datetime
from sqlalchemy import Column, String, Boolean, DateTime, BigInteger, Text
import common.orm


class MailQueue(common.orm.sql_base):

    __tablename__ = 'mail_queue'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    subject = Column(String(128), index=True, nullable=False)
    sender_name = Column(String(128), nullable=False)
    sender = Column(String(128), index=True, nullable=False)
    receiver_name = Column(String(128), nullable=False)
    receiver = Column(String(128), nullable=False)
    time_created = Column(DateTime, nullable=False, default=datetime.datetime.now())
    time_sent = Column(DateTime)
    sent = Column(Boolean, index=True, nullable=False, default=True)
    message = Column(Text, nullable=False)
    data = Column(Text)

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
