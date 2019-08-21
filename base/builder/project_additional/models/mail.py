# coding= utf-8
import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text
import base.common.orm


class MailQueue(base.common.orm.sql_base):

    __tablename__ = 'mail_queue'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject = Column(String(128), index=True, nullable=False)
    sender_name = Column(String(128), nullable=False)
    sender = Column(String(128), index=True, nullable=False)
    receiver_name = Column(String(128), nullable=False)
    receiver = Column(String(128), nullable=False)
    time_created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    time_sent = Column(DateTime)
    sent = Column(Boolean, index=True, nullable=False, default=True)
    message = Column(Text, nullable=False)
    data = Column(Text)

    def __init__(self, sender, sender_name, receiver, receiver_name, subject, message, data=None, sent=True):

        self.sender = sender
        self.sender_name = sender_name
        if not self.sender_name:
            self.sender_name = sender
        self.receiver = receiver
        self.receiver_name = receiver_name
        if not self.receiver_name:
            self.receiver_name = receiver
        self.subject = subject
        self.message = message
        self.data = data
        self.sent = sent


def main():
    pass


if __name__ == '__main__':

    main()
