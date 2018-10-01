# coding= utf-8

from sqlalchemy import Column, String, Integer, Text
import base.common.orm


class Page(base.common.orm.sql_base):
    """Site page data"""

    __tablename__ = 'site_page'

    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(String(64), unique=True, nullable=False)
    html_meta = Column(Text(), nullable=False)

    def __init__(self, url, html_meta):
        self.url = url
        self.html_meta = html_meta


def main():
    pass


if __name__ == '__main__':
    main()
