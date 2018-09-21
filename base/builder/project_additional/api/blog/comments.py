# coding= utf-8

from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.application.components import authenticated

from src.common.common import add_comment
from src.common.common import get_comments
from src.common.common import change_comment_status


@api(
    URI='/wiki/posts/:id_post/authorized/comments',
    SPECIFICATION_PATH='Blog'
)
@authenticated()
class AuthorizedComment(Base):

    @params(
        {'name': 'id_post', 'type': str, 'doc': 'id', 'required': True},
        {'name': 'text', 'type': str, 'doc': 'comment', 'required': False},
        {'name': 'id_parent_comment', 'type': int, 'doc': 'id_parent_comment', 'required': False},
    )
    def put(self, id_post, text, id_parent_comment):
        return add_comment(id_post, text, id_parent_comment, self.auth_user.user, None, None, self)


@api(
    URI='/wiki/posts/:id_post/comments',
    SPECIFICATION_PATH='Blog'
)
class UnauthorizedComment(Base):

    @params(
        {'name': 'id_post', 'type': str, 'doc': 'id', 'required': True},
        {'name': 'text', 'type': str, 'doc': 'comment', 'required': False},
        {'name': 'email', 'type': 'e-mail', 'doc': 'email', 'required': False},
        {'name': 'display_name', 'type': str, 'doc': 'email', 'required': False},
        {'name': 'id_parent_comment', 'type': int, 'doc': 'id_parent_comment', 'required': False},
    )
    def put(self, id_post, text, email, display_name, id_parent_comment):
        return add_comment(id_post, text, id_parent_comment, None, email.lower() if email else None, display_name, self)

    @params(
        {'name': 'id_post', 'type': str, 'doc': 'id', 'required': True},
        {'name': 'canonical', 'type': bool, 'doc': 'canonical', 'requested': False, 'default': False}
    )
    def get(self, id_post, canonical):
        successfull, res = get_comments(id_post, canonical)

        if not successfull:
            return self.error(res)

        return self.ok({'comments': res})

@api(
    URI='/wiki/cps',
    SPECIFICATION_PATH='Blog'
)
class ChangeStatusComment(Base):

    @params(
        {'name': 'approved', 'type': bool, 'doc': 'status of comment', 'required': True},
        {'name': 'id_post', 'type': str, 'doc': 'id post', 'required': True},
        {'name': 'id_comment', 'type': str, 'doc': 'id comment', 'required': True},
    )
    def patch(self, approved, id_post, id_comment):

        return change_comment_status(approved, id_post, id_comment, self)




