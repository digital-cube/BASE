# coding= utf-8

import hashlib

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Text, ForeignKey, CHAR, VARCHAR

import base.common.orm
from base.common.utils import get_request_ip

from src.models.user import User


class ActionSource(base.common.orm.sql_base):
    __tablename__ = 'action_source'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(VARCHAR(16), nullable=False)
    browser_info = Column(Text)
    ip_browser_checksum = Column(VARCHAR(32), index=True)
    action = relationship('Action', back_populates='source')

    def __init__(self, ip, browser_info):

        self.ip = ip
        self.browser_info = browser_info
        self.ip_browser_checksum = self.ipbcs(ip, browser_info)

    def ipbcs(self, ip, bi):
        return hashlib.md5(str(ip+bi).encode('utf-8')).hexdigest()


class Action(base.common.orm.sql_base):
    __tablename__ = 'actions'

    id = Column(Integer, primary_key=True, autoincrement=True)

    id_user = Column(CHAR(10), ForeignKey(User.id), index=True)
    action = Column(VARCHAR(16), nullable=False)
    description = Column(VARCHAR(255))
    user = relationship(User)
    id_source = Column(Integer, ForeignKey(ActionSource.id), index=True)
    source = relationship(ActionSource, back_populates='action')

    def __init__(self, action, description, controller, source):
        ua = controller.request.headers['User-Agent'] if 'User-Agent' in controller.request.headers else 'User-Agent N/A'
        ip = get_request_ip(controller)
        self.action = action
        self.description = description
        self.source = source


def main():
    pass


if __name__ == '__main__':

    main()

