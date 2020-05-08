# coding= utf-8
import json

from base.common.utils import log
from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.application.components import authenticated


@authenticated()
@api(
    URI='/site/page',
    SPECIFICATION_PATH='Site'
)
class Page(Base):

    @params(
        {'name': 'url', 'type': str, 'doc': 'page url', 'required': True},
    )
    def get(self, page_url):
        OrmPage = base.common.orm.get_orm_model('site_page')
        _page = self.orm_session.query(OrmPage).filter(OrmPage.url == page_url).one_or_none()
        _page_meta = '' if _page is None else json.loads(_page.html_meta)['html_meta']

        return self.ok({'page_meta': _page_meta})

    @params(
        {'name': 'url', 'type': str, 'doc': 'page url', 'required': True},
        {'name': 'html_meta', 'type': json, 'doc': 'page meta', 'required': True}
    )
    def put(self, page_url, html_meta):
        OrmPage = base.common.orm.get_orm_model('site_page')
        _page = self.orm_session.query(OrmPage).filter(OrmPage.url == page_url).one_or_none()

        try:
            _html_meta = json.dumps({'html_meta': html_meta})
        except Exception as e:
            log.critical('Error save data; {}'.format(e))
            return self.error('Error save page data')

        if _page is None:
            _page = OrmPage(page_url, _html_meta)
            self.orm_session.add(_page)
        else:
            _page.html_meta = _html_meta

        self.orm_session.commit()

        return self.ok({'id': _page.id})
