from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from base.orm import sql_base, BaseSql
from sqlalchemy import Text

import os

current_file_folder = os.path.dirname(os.path.realpath(__file__))


class Mailqueue(BaseSql, sql_base):
    __tablename__ = 'mail_queue'

    id = Column(UUID, primary_key=True)

    sender_name = Column(String, nullable=True)
    sender_email = Column(String, nullable=False)

    id_receiver = Column(UUID, nullable=True)
    receiver_name = Column(String, nullable=True)
    receiver_email = Column(String, nullable=False)

    subject = Column(String, nullable=True)
    body = Column(Text, nullable=True)

    response_status = Column(String)
    sent_timestamp = Column(DateTime)

    def __init__(self, sender_email, receiver_email, subject, body, sender_name=None, id_receiver=None,
                 receiver_name=None):
        super().__init__()
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.id_receiver = id_receiver
        self.receiver_name = receiver_name
        self.receiver_email = receiver_email
        self.subject = subject
        self.body = body
