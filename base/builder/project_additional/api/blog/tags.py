# coding= utf-8

from base.application.components import Base
from base.application.components import api
from base.application.components import authenticated

from src.models.knowledgebase import PostCategory, Tag


@authenticated()
@api(
    URI='/wiki/tags'
)
class GetAllTags(Base):

    def get(self):
        import base.common.orm
        return self.ok({'tags': Tag.all(base.common.orm.orm.session())})


@authenticated()
@api(
    URI='/wiki/categories'
)
class GetAllCategories(Base):

    def get(self):
        import base.common.orm
        return self.ok({'categories': PostCategory.all(base.common.orm.orm.session())})

