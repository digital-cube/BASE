# coding= utf-8

from base.application.components import Base
from base.application.components import api
from base.application.components import authenticated

from src.models.blog import PostCategory, Tag, ShowTag


@authenticated()
@api(
    URI='/wiki/tags',
    SPECIFICATION_PATH='Blog'
)
class GetAllTags(Base):

    def get(self):
        import base.common.orm
        return self.ok({'tags': Tag.all(base.common.orm.orm.session())})


@authenticated()
@api(
    URI='/wiki/show-tags',
    SPECIFICATION_PATH='Blog'
)
class GetAllShowTags(Base):

    def get(self):
        import base.common.orm
        return self.ok({'show_tags': ShowTag.all(base.common.orm.orm.session())})


@authenticated()
@api(
    URI='/wiki/categories',
    SPECIFICATION_PATH='Blog'
)
class GetAllCategories(Base):

    def get(self):
        import base.common.orm
        return self.ok({'categories': PostCategory.all(base.common.orm.orm.session())})

